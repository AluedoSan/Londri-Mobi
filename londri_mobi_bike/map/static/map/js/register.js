// Referências aos elementos
const abrirTermos = document.getElementById('abrir-termos');
const popupTermos = document.getElementById('popup-termos');
const fecharPopup = document.getElementById('fechar-popup');

// Abrir o pop-up ao clicar no link
abrirTermos.addEventListener('click', function(event) {
    event.preventDefault(); // Evitar que o link recarregue a página
    popupTermos.style.display = 'flex'; // Mostrar o pop-up
});

// Fechar o pop-up ao clicar no "x"
fecharPopup.addEventListener('click', function() {
    popupTermos.style.display = 'none';
});

// Fechar o pop-up ao clicar fora da caixa de conteúdo
window.addEventListener('click', function(event) {
    if (event.target === popupTermos) {
        popupTermos.style.display = 'none';
    }
});
// Função para validar se as senhas são iguais
function checkPasswordMatch() {
    const password = document.getElementById('password');
    const passwordConfirm = document.getElementById('password_confirm');
    const errorMessage = document.getElementById('error-message');

    // Verificar se as senhas são diferentes
    if (password.value !== passwordConfirm.value) {
        errorMessage.style.display = 'block'; // Exibir mensagem de erro
        passwordConfirm.setCustomValidity('As senhas não coincidem'); // Definir mensagem de erro
    } else {
        errorMessage.style.display = 'none'; // Ocultar mensagem de erro
        passwordConfirm.setCustomValidity(''); // Limpar mensagem de erro
    }
}
