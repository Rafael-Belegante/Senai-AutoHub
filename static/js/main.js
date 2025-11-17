
// Validação simples de formulário e ganchos futuros

document.addEventListener("submit", function (event) {
    const form = event.target;
    if (form.matches("[data-requires-csrf]")) {
        const tokenInput = form.querySelector("input[name='_csrf']");
        if (!tokenInput || !tokenInput.value) {
            event.preventDefault();
            alert("Falha de segurança: token CSRF ausente.");
        }
    }
});
