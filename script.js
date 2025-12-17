// @ts-nocheck
function configurarLed() {
  const botaoLed = document.getElementById('ledBtn');

  if (botaoLed instanceof HTMLButtonElement) {
    // Inicializa o estado no próprio botão, se ainda não estiver definido
    if (!botaoLed.dataset.estado) {
      botaoLed.dataset.estado = 'off';
    }

    botaoLed.addEventListener('click', () => {
      alternarEstadoLed(botaoLed);
    });
  }
}

function alternarEstadoLed(botao) {
  const estadoAtual = botao.dataset.estado === 'on';

  if (estadoAtual) {
    botao.dataset.estado = 'off';
    atualizarBotao(botao, 'OFF', 'on', 'off');
    fetch('/2/off');
  } else {
    botao.dataset.estado = 'on';
    atualizarBotao(botao, 'ON', 'off', 'on');
    fetch('/2/on');
  }
}

function atualizarBotao(botao, texto, classeRemover, classeAdicionar) {
  botao.textContent = texto;
  botao.classList.remove(classeRemover);
  botao.classList.add(classeAdicionar);
}

document.addEventListener('DOMContentLoaded', configurarLed);
