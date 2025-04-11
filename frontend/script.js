// URLs de los servicios (ajusta según tu configuración)
const citizen1Url = 'http://10.173.8.113:5001';
const citizen2Url = 'http://10.173.8.113:5002';
const frontendUrl = 'http://10.173.8.114:9000';

// Función para enviar mensajes
async function sendMessage(citizenId) {
    const messageInput = document.getElementById(`message${citizenId}`);
    const message = messageInput.value;
    
    if (!message) return;
    
    try {
        const response = await fetch(`${citizenId === 1 ? citizen1Url : citizen2Url}/send/${message}`);
        const data = await response.json();
        
        logMessage(citizenId, message, 'sent');
        messageInput.value = '';
        
        // Actualizar las vistas de la base de datos
        updateVotesView();
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

// Función para registrar mensajes en el log
function logMessage(citizenId, message, direction) {
    const messageLog = document.getElementById('messageLog');
    const messageElement = document.createElement('div');
    messageElement.className = `message citizen${citizenId}`;
    
    const directionText = direction === 'sent' ? 'sent to' : 'received from';
    messageElement.textContent = `Citizen ${citizenId} ${directionText} Citizen ${citizenId === 1 ? 2 : 1}: ${message}`;
    
    messageLog.appendChild(messageElement);
    messageLog.scrollTop = messageLog.scrollHeight;
}

// Función para actualizar la vista de votos
async function updateVotesView() {
    try {
        // Obtener votos de Citizen 1
        const response1 = await fetch(`${citizen1Url}/votes`);
        const votes1 = await response1.json();
        displayVotes('votes1', votes1);
        
        // Obtener votos de Citizen 2
        const response2 = await fetch(`${citizen2Url}/votes`);
        const votes2 = await response2.json();
        displayVotes('votes2', votes2);
    } catch (error) {
        console.error('Error updating votes:', error);
    }
}

// Función para mostrar votos en el contenedor especificado
function displayVotes(containerId, votes) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    votes.forEach(vote => {
        const voteElement = document.createElement('div');
        voteElement.className = 'vote-entry';
        
        const [id, citizenId, message, timestamp] = vote;
        voteElement.textContent = `ID: ${id} | Vote: ${message} | Time: ${timestamp}`;
        
        container.appendChild(voteElement);
    });
}

// Simular recepción de mensajes (en un entorno real usarías WebSockets)
setInterval(updateVotesView, 2000);

// Inicializar la vista al cargar la página
document.addEventListener('DOMContentLoaded', updateVotesView);
