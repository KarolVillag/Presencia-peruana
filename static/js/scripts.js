document.addEventListener("DOMContentLoaded", () => {

    // --- Carrusel (solo si existe) ---
    const carousel = document.querySelector(".carousel");
    const prevBtn = document.querySelector(".prev");
    const nextBtn = document.querySelector(".next");
    if (carousel && prevBtn && nextBtn) {
        const scrollAmount = carousel.clientWidth;
        prevBtn.addEventListener("click", () => {
            carousel.scrollBy({ left: -scrollAmount, behavior: "smooth" });
        });
        nextBtn.addEventListener("click", () => {
            carousel.scrollBy({ left: scrollAmount, behavior: "smooth" });
        });
    }

    // --- Chat (solo si existe) ---
    const chatBody = document.getElementById("chat-body");
    const chatOptions = document.getElementById("chat-options");
    const chatToggle = document.getElementById("chat-toggle");
    const chatbot = document.getElementById("chatbot");

    if (chatBody && chatOptions && chatToggle && chatbot) {

        const opciones = [
            { text: "1. Ver menú del día", value: "1" },
            { text: "2. Recomendación de plato", value: "2" },
            { text: "3. Opiniones de clientes", value: "3" },
            { text: "4. Estadísticas de ventas", value: "4" },
            { text: "5. Promoción especial", value: "5" }
        ];

        function addMessage(msg, isImage=false) {
            const div = document.createElement("div");
            if (isImage) {
                const img = document.createElement("img");
                img.src = msg;
                img.style.maxWidth = "100%";
                div.appendChild(img);
            } else {
                div.innerHTML = msg;
            }
            chatBody.appendChild(div);
            chatBody.scrollTop = chatBody.scrollHeight;
        }

        function showOptions(options) {
            chatOptions.innerHTML = "";
            options.forEach(opt => {
                const btn = document.createElement("button");
                btn.textContent = opt.text;
                btn.onclick = () => enviarOpcion(opt.value);
                chatOptions.appendChild(btn);
            });
        }

        function enviarOpcion(opcion) {
            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ opcion: opcion })
            })
            .then(res => res.json())
            .then(data => {
                if (data.respuesta) {
                    if (Array.isArray(data.respuesta)) {
                        const menuTexto = data.respuesta
                            .map(item => `${item.plato} - S/.${item.precio}`)
                            .join("<br>");
                        addMessage(menuTexto);
                    } else {
                        addMessage(data.respuesta);
                    }
                }
                if (data.imagen) {
                    addMessage(data.imagen, true);
                }
            });
        }

        addMessage("¡Hola! Soy tu asistente de Presencia Peruana. <br> Elige una opción:<br>");
        showOptions(opciones);

        chatToggle.addEventListener("click", () => {
            chatbot.classList.toggle("hidden");
        });
    }

    // --- Menu Responsive ---
    const navToggle = document.getElementById('nav-toggle');
    const navUl = document.getElementById('nav-links');

    if (navToggle && navUl) {
        navToggle.addEventListener('click', () => {
            navUl.classList.toggle('active');
        });

        navUl.querySelectorAll('li a').forEach(link => {
            link.addEventListener('click', () => {
                navUl.classList.remove('active');
            });
        });
    }

});