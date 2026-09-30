(function () {
    "use strict";

    const panel = document.getElementById("chat");
    const log = document.getElementById("chat-log");
    const form = document.getElementById("chat-form");
    const campo = document.getElementById("texto");
    if (!panel || !log || !form || !campo) {
        return;
    }

    const usuario = panel.dataset.usuario;
    let ultimo = panel.dataset.ultimo || "0";
    let socket = null;
    let sondeo = null;

    function csrf() {
        const input = form.querySelector("[name=csrfmiddlewaretoken]");
        return input ? input.value : "";
    }

    function burbuja(mensaje) {
        const previa = log.querySelector("[data-id='" + mensaje.id + "']");
        if (previa) {
            return;
        }
        const vacio = document.getElementById("chat-vacio");
        if (vacio) {
            vacio.remove();
        }
        const articulo = document.createElement("article");
        articulo.className = "bubble " + (String(mensaje.remitente_id) === usuario ? "propia" : "ajena");
        articulo.dataset.id = mensaje.id;
        const texto = document.createElement("p");
        texto.className = "bubble-text";
        texto.textContent = mensaje.texto;
        const meta = document.createElement("p");
        meta.className = "meta";
        const hora = document.createElement("time");
        hora.textContent = mensaje.hora;
        meta.appendChild(hora);
        if (String(mensaje.remitente_id) === usuario) {
            const estado = document.createElement("span");
            estado.className = "lectura";
            estado.textContent = mensaje.leido ? "Leído" : "Enviado";
            meta.appendChild(document.createTextNode(" "));
            meta.appendChild(estado);
        }
        articulo.appendChild(texto);
        articulo.appendChild(meta);
        log.appendChild(articulo);
        ultimo = String(mensaje.id);
        log.scrollTop = log.scrollHeight;
    }

    function marcarLeidos() {
        log.querySelectorAll(".bubble.propia .lectura").forEach(function (nodo) {
            nodo.textContent = "Leído";
        });
    }

    const estado = document.getElementById("chat-estado");

    function mostrarEstado(modo, texto) {
        if (!estado) {
            return;
        }
        estado.dataset.modo = modo;
        estado.textContent = texto;
    }

    function sondear() {
        if (sondeo) {
            return;
        }
        mostrarEstado("sondeo", "Actualizando cada pocos segundos");
        sondeo = window.setInterval(function () {
            fetch(panel.dataset.leer + "?despues=" + encodeURIComponent(ultimo) + "&leer=1", {
                headers: { Accept: "application/json" },
                credentials: "same-origin",
            })
                .then(function (respuesta) {
                    return respuesta.json();
                })
                .then(function (datos) {
                    (datos.mensajes || []).forEach(burbuja);
                })
                .catch(function () {});
        }, 3000);
    }

    function conectar() {
        const protocolo = window.location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(protocolo + "://" + window.location.host + "/ws/chat/" + panel.dataset.conversacion + "/");
        socket.onmessage = function (evento) {
            let datos;
            try {
                datos = JSON.parse(evento.data);
            } catch (error) {
                return;
            }
            if (datos.mensaje) {
                burbuja(datos.mensaje);
            }
            if (datos.leido_por && String(datos.leido_por) !== usuario) {
                marcarLeidos();
            }
            if (datos.error) {
                window.alert(datos.error);
            }
        };
        socket.onopen = function () {
            mostrarEstado("vivo", "En tiempo real");
            socket.send(JSON.stringify({ accion: "leer" }));
        };
        socket.onerror = function () {
            socket.close();
        };
        socket.onclose = function () {
            socket = null;
            sondear();
        };
    }

    function enviar(texto) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ accion: "enviar", texto: texto }));
            campo.value = "";
            return;
        }
        const cuerpo = new FormData();
        cuerpo.append("texto", texto);
        cuerpo.append("csrfmiddlewaretoken", csrf());
        fetch(panel.dataset.enviar, {
            method: "POST",
            body: cuerpo,
            headers: { "X-Requested-With": "fetch" },
            credentials: "same-origin",
        })
            .then(function (respuesta) {
                return respuesta.json().then(function (datos) {
                    return { ok: respuesta.ok, datos: datos };
                });
            })
            .then(function (resultado) {
                if (!resultado.ok) {
                    window.alert(resultado.datos.error || "No se pudo enviar.");
                    return;
                }
                burbuja(resultado.datos.mensaje);
                campo.value = "";
            })
            .catch(function () {
                form.submit();
            });
    }

    form.addEventListener("submit", function (evento) {
        evento.preventDefault();
        const texto = campo.value.trim();
        if (!texto) {
            return;
        }
        enviar(texto);
    });

    campo.addEventListener("keydown", function (evento) {
        if (evento.key === "Enter" && !evento.shiftKey) {
            evento.preventDefault();
            form.requestSubmit();
        }
    });

    conectar();
    log.scrollTop = log.scrollHeight;
})();
