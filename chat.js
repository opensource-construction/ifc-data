document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const ifcFileInput = document.getElementById('ifc-file-input');
  const messageInput = document.getElementById('message-input');
  const messages = document.getElementById('messages');

  form.addEventListener('submit', async (event) => {
      event.preventDefault();

      const ifcFile = ifcFileInput.files[0];
      const message = messageInput.value.trim();

      if (!message || !ifcFile) {
          return;
      }

      try {
          const ifcContent = await readFileAsDataURL(ifcFile);
          const response = await sendMessage(message, ifcContent);
          messages.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
          messages.innerHTML += `<div><strong>Bot:</strong> ${response}</div>`;
          messageInput.value = '';
      } catch (error) {
          console.error('Error in sendMessage:', error);
      }
  });
});

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
  });
}

async function sendMessage(message, ifcContent) {
  const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          prompt: message,
          ifc_content: ifcContent,
      }),
  });

  if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
  }

  const data = await response.json();

  if (data.error) {
      throw new Error(data.error);
  }

  return data.response;
}


async function sendMessage(message, ifcContent) {
  const response = await fetch('http://127.0.0.1:5001/api/chat', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          prompt: message,
          ifc_content: ifcContent,
      }),
  });

  if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
  }

  const data = await response.json();

  if (data.error) {
      throw new Error(data.error);
  }

  return data.response;
}
