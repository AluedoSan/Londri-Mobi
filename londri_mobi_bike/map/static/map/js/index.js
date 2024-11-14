
window.onload = function() {
    const mapContainer = document.getElementById("map-container");

    // Verifica se o mapa está carregado corretamente
    if (!mapContainer.innerHTML.trim()) {
        // Força o reload da página se o mapa não estiver carregado
        setTimeout(() => {
            window.location.reload();
        }, 500); // Aguarda meio segundo para evitar loops infinitos
    }
};