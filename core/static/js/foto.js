(function () {
    "use strict";

    const dialog = document.getElementById("foto-dialog");
    const form = document.getElementById("foto-form");
    const lienzo = document.getElementById("foto-lienzo");
    const stage = document.getElementById("foto-stage");
    const archivo = document.getElementById("foto-archivo");
    const movil = document.getElementById("foto-movil");
    const video = document.getElementById("foto-video");
    const zoom = document.getElementById("foto-zoom");
    const campo = document.getElementById("foto-campo");
    const campoQuitar = document.getElementById("foto-campo-quitar");
    const permiso = document.getElementById("foto-permiso");
    const capturar = document.getElementById("foto-capturar");
    const repetir = document.getElementById("foto-repetir");
    const eliminar = document.getElementById("foto-eliminar");
    const ayuda = document.getElementById("foto-ayuda");
    const titulo = document.getElementById("foto-titulo");
    if (!dialog || !form || !lienzo || !archivo) {
        return;
    }

    const ctx = lienzo.getContext("2d");
    let imagen = null;
    let desplazamiento = { x: 0, y: 0 };
    let arrastre = null;
    let stream = null;
    let modo = "foto";

    function marco() {
        if (modo === "portada") {
            return { ancho: 360, alto: 120 };
        }
        return { ancho: 360, alto: 360 };
    }

    function aplicarMarco() {
        const medidas = marco();
        lienzo.width = medidas.ancho;
        lienzo.height = medidas.alto;
        stage.classList.toggle("circular", modo === "foto");
        dibujar();
    }

    function escalaBase() {
        const medidas = marco();
        return Math.max(medidas.ancho / imagen.width, medidas.alto / imagen.height);
    }

    function dibujar() {
        const medidas = marco();
        ctx.clearRect(0, 0, medidas.ancho, medidas.alto);
        if (!imagen) {
            return;
        }
        const escala = escalaBase() * Number(zoom.value || 1);
        const ancho = imagen.width * escala;
        const alto = imagen.height * escala;
        const x = (medidas.ancho - ancho) / 2 + desplazamiento.x;
        const y = (medidas.alto - alto) / 2 + desplazamiento.y;
        ctx.drawImage(imagen, x, y, ancho, alto);
    }

    function mostrarRecorte(origen) {
        imagen = origen;
        desplazamiento = { x: 0, y: 0 };
        zoom.value = "1";
        stage.hidden = false;
        aplicarMarco();
    }

    function leerArchivo(file) {
        if (!file) {
            return;
        }
        const lector = new FileReader();
        lector.onload = function () {
            const foto = new Image();
            foto.onload = function () {
                mostrarRecorte(foto);
            };
            foto.src = lector.result;
        };
        lector.readAsDataURL(file);
    }

    function pararCamara() {
        if (stream) {
            stream.getTracks().forEach(function (pista) {
                pista.stop();
            });
            stream = null;
        }
        video.srcObject = null;
        video.hidden = true;
        capturar.hidden = true;
    }

    function iniciarCamara() {
        permiso.hidden = true;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            permiso.hidden = false;
            return;
        }
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false })
            .then(function (medio) {
                stream = medio;
                video.srcObject = medio;
                video.hidden = false;
                capturar.hidden = false;
                repetir.hidden = true;
                permiso.hidden = true;
            })
            .catch(function () {
                video.hidden = true;
                capturar.hidden = true;
                permiso.hidden = false;
            });
    }

    function pestana(nombre) {
        const subir = nombre === "subir";
        document.getElementById("foto-panel-subir").hidden = !subir;
        document.getElementById("foto-panel-camara").hidden = subir;
        document.getElementById("foto-tab-subir").setAttribute("aria-selected", subir ? "true" : "false");
        document.getElementById("foto-tab-camara").setAttribute("aria-selected", subir ? "false" : "true");
        if (subir) {
            pararCamara();
        } else if (!imagen) {
            iniciarCamara();
        }
    }

    function abrir(boton) {
        modo = boton.getAttribute("data-foto-open") === "portada" ? "portada" : "foto";
        campo.value = modo;
        campoQuitar.value = modo;
        titulo.textContent = modo === "portada" ? "Cambiar portada" : "Cambiar foto de perfil";
        ayuda.textContent = modo === "portada"
            ? "La portada es panorámica, cerca de tres veces más ancha que alta."
            : "La foto se guarda en cuadrado y se muestra en círculo.";
        eliminar.hidden = boton.getAttribute("data-tiene") !== "1";
        imagen = null;
        stage.hidden = true;
        archivo.value = "";
        repetir.hidden = true;
        pestana("subir");
        dialog.showModal();
    }

    document.querySelectorAll("[data-foto-open]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            abrir(boton);
        });
    });

    document.getElementById("foto-cerrar").addEventListener("click", function () {
        dialog.close();
    });
    dialog.addEventListener("close", pararCamara);
    document.getElementById("foto-tab-subir").addEventListener("click", function () {
        pestana("subir");
    });
    document.getElementById("foto-tab-camara").addEventListener("click", function () {
        pestana("camara");
    });
    archivo.addEventListener("change", function () {
        leerArchivo(archivo.files && archivo.files[0]);
    });
    movil.addEventListener("change", function () {
        leerArchivo(movil.files && movil.files[0]);
    });
    zoom.addEventListener("input", dibujar);

    lienzo.addEventListener("pointerdown", function (evento) {
        if (!imagen) {
            return;
        }
        arrastre = { x: evento.clientX, y: evento.clientY, ox: desplazamiento.x, oy: desplazamiento.y };
        lienzo.setPointerCapture(evento.pointerId);
    });
    lienzo.addEventListener("pointermove", function (evento) {
        if (!arrastre) {
            return;
        }
        desplazamiento.x = arrastre.ox + (evento.clientX - arrastre.x);
        desplazamiento.y = arrastre.oy + (evento.clientY - arrastre.y);
        dibujar();
    });
    lienzo.addEventListener("pointerup", function () {
        arrastre = null;
    });

    capturar.addEventListener("click", function () {
        if (!video.videoWidth) {
            return;
        }
        const captura = document.createElement("canvas");
        captura.width = video.videoWidth;
        captura.height = video.videoHeight;
        captura.getContext("2d").drawImage(video, 0, 0);
        const foto = new Image();
        foto.onload = function () {
            mostrarRecorte(foto);
            pararCamara();
            repetir.hidden = false;
        };
        foto.src = captura.toDataURL("image/jpeg", 0.92);
    });

    repetir.addEventListener("click", function () {
        imagen = null;
        stage.hidden = true;
        repetir.hidden = true;
        iniciarCamara();
    });

    form.addEventListener("submit", function (evento) {
        if (!imagen) {
            if (archivo.files && archivo.files.length) {
                return;
            }
            evento.preventDefault();
            window.alert("Elige o toma una imagen antes de guardar.");
            return;
        }
        evento.preventDefault();
        const salida = document.createElement("canvas");
        const medidas = marco();
        const destinoAncho = modo === "portada" ? 1500 : 512;
        const destinoAlto = modo === "portada" ? 500 : 512;
        salida.width = destinoAncho;
        salida.height = destinoAlto;
        const factor = destinoAncho / medidas.ancho;
        const escala = escalaBase() * Number(zoom.value || 1);
        const ancho = imagen.width * escala * factor;
        const alto = imagen.height * escala * factor;
        const x = ((medidas.ancho - imagen.width * escala) / 2 + desplazamiento.x) * factor;
        const y = ((medidas.alto - imagen.height * escala) / 2 + desplazamiento.y) * factor;
        salida.getContext("2d").drawImage(imagen, x, y, ancho, alto);
        salida.toBlob(function (blob) {
            const datos = new FormData();
            datos.append("csrfmiddlewaretoken", form.querySelector("[name=csrfmiddlewaretoken]").value);
            datos.append("campo", modo);
            datos.append("imagen", blob, "recorte.jpg");
            fetch(form.action, {
                method: "POST",
                body: datos,
                headers: { "X-Requested-With": "fetch" },
                credentials: "same-origin",
            })
                .then(function (respuesta) {
                    return respuesta.json().then(function (cuerpo) {
                        return { ok: respuesta.ok, cuerpo: cuerpo };
                    });
                })
                .then(function (resultado) {
                    if (!resultado.ok) {
                        window.alert(resultado.cuerpo.error || "No se pudo guardar la imagen.");
                        return;
                    }
                    window.location.reload();
                })
                .catch(function () {
                    form.submit();
                });
        }, "image/jpeg", 0.9);
    });
})();
