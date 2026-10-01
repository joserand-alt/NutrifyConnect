import os, re

def apply_audio_patch():
    template_path = 'template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Inserir botão de Áudio no Header ao lado do chip de 48H
    target_chip = '<div class="hud-api-chip" onclick="openModalSync24h()"'
    if target_chip not in html:
        print("Target chip not found in template.html!")
        return False

    sound_btn_html = '''<!-- CHIP DE NOTIFICAÇÕES SONORAS (VITÓRIA & OPORTUNIDADE) -->
      <div id="hud-sound-btn" class="hud-api-chip" onclick="toggleSoundNotifications()" title="Clique para Ativar/Silenciar sons de Vitória e Oportunidade" style="display:flex; align-items:center; gap:5px; padding:4px 9px; border-radius:6px; background:rgba(234,179,8,0.15); border:1px solid rgba(234,179,8,0.5); font-size:10.5px; font-family:var(--font-mono); cursor:pointer; transition:all 0.2s;" onmouseover="this.style.transform='scale(1.04)'" onmouseout="this.style.transform='scale(1)'">
        <span id="sound-icon" style="font-size:12px;">🔊</span>
        <b id="sound-text" style="color:#fde047;">ÁUDIO: ON</b>
        <span onclick="event.stopPropagation(); testVictorySound();" title="Testar Som de Vitória (Videogame) 🎮" style="cursor:pointer; margin-left:4px; padding:1px 4px; border-radius:3px; background:rgba(16,185,129,0.3); border:1px solid #10b981; font-size:9.5px; color:#34d399;" onmouseover="this.style.filter='brightness(1.3)'" onmouseout="this.style.filter='none'">🎮 TESTAR</span>
        <span onclick="event.stopPropagation(); testOpportunitySound();" title="Testar Som de Oportunidade (Pendente) ⚡" style="cursor:pointer; margin-left:2px; padding:1px 4px; border-radius:3px; background:rgba(245,158,11,0.3); border:1px solid #f59e0b; font-size:9.5px; color:#fbbf24;" onmouseover="this.style.filter='brightness(1.3)'" onmouseout="this.style.filter='none'">⚡ PENDENTE</span>
      </div>

      '''

    if 'id="hud-sound-btn"' not in html:
        html = html.replace(target_chip, sound_btn_html + target_chip, 1)
        print("[OK] Botao de som inserido no Header!")
    else:
        print("[INFO] Botao de som ja existe no Header.")

    # 2. Inserir o script do Sistema de Áudio e Notificações antes de </body> ou no final do arquivo
    audio_system_js = '''
<!-- ============================================================ -->
<!-- SISTEMA OFICIAL DE AUDIO & NOTIFICACOES (VITORIA & OPORTUNIDADE) -->
<!-- ============================================================ -->
<script>
(function() {
    let audioCtx = null;
    let soundEnabled = (localStorage.getItem('infecto_sound_enabled') !== 'false');

    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    // Desbloqueia contexto de audio em qualquer interacao do usuario
    document.addEventListener('click', function unlockAudio() {
        getAudioContext();
    }, { passive: true });

    // 1. SOM DE VITORIA / VIDEOGAME (Matricula Confirmada / Venda Aprovada)
    // Fanfarra arpejada em 8-bit estilo conquista de videogame (Super Mario / Level Up / Victory)
    window.playVictorySound = function() {
        if (!soundEnabled) return;
        try {
            const ctx = getAudioContext();
            if (!ctx) return;
            const now = ctx.currentTime;

            const masterGain = ctx.createGain();
            masterGain.gain.setValueAtTime(0.28, now);
            masterGain.connect(ctx.destination);

            // Notas do arpeggio ascendente triunfal de videogame
            const notes = [
                { f: 523.25, t: 0.00, d: 0.09, type: 'triangle' }, // C5
                { f: 659.25, t: 0.08, d: 0.09, type: 'triangle' }, // E5
                { f: 783.99, t: 0.16, d: 0.09, type: 'triangle' }, // G5
                { f: 1046.50, t: 0.24, d: 0.11, type: 'square' },   // C6
                { f: 1318.51, t: 0.34, d: 0.13, type: 'square' },   // E6
                { f: 1567.98, t: 0.46, d: 0.50, type: 'sine' }      // G6
            ];

            notes.forEach(n => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.type = n.type;
                osc.frequency.setValueAtTime(n.f, now + n.t);

                gain.gain.setValueAtTime(0.001, now + n.t);
                gain.gain.exponentialRampToValueAtTime(0.35, now + n.t + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);

                osc.connect(gain);
                gain.connect(masterGain);

                osc.start(now + n.t);
                osc.stop(now + n.t + n.d + 0.05);
            });

            // Acorde harmonico estendido de celebracao (C-Major Chord)
            const chord = [1046.50, 1318.51, 1567.98, 2093.00];
            chord.forEach(f => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, now + 0.46);
                gain.gain.setValueAtTime(0.001, now + 0.46);
                gain.gain.exponentialRampToValueAtTime(0.15, now + 0.48);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.25);
                osc.connect(gain);
                gain.connect(masterGain);
                osc.start(now + 0.46);
                osc.stop(now + 1.30);
            });
        } catch (e) {
            console.warn('Erro ao reproduzir som de vitoria:', e);
        }
    };

    // 2. SOM DE ATENCAO / OPORTUNIDADE (Matricula Pendente / Lead Novo na Plataforma)
    // Tom duplo elegante de radar/sino de oportunidade (Ping-Ding suave e cristalino)
    window.playOpportunitySound = function() {
        if (!soundEnabled) return;
        try {
            const ctx = getAudioContext();
            if (!ctx) return;
            const now = ctx.currentTime;

            const masterGain = ctx.createGain();
            masterGain.gain.setValueAtTime(0.28, now);
            masterGain.connect(ctx.destination);

            // Tom 1: Atencao (F5 - 698.46 Hz)
            const osc1 = ctx.createOscillator();
            const gain1 = ctx.createGain();
            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(698.46, now);
            gain1.gain.setValueAtTime(0.001, now);
            gain1.gain.exponentialRampToValueAtTime(0.30, now + 0.02);
            gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.20);
            osc1.connect(gain1);
            gain1.connect(masterGain);
            osc1.start(now);
            osc1.stop(now + 0.22);

            // Tom 2: Sino de oportunidade ressonante (C6 - 1046.50 Hz)
            const osc2 = ctx.createOscillator();
            const gain2 = ctx.createGain();
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(1046.50, now + 0.10);
            gain2.gain.setValueAtTime(0.001, now + 0.10);
            gain2.gain.exponentialRampToValueAtTime(0.35, now + 0.13);
            gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.90);
            osc2.connect(gain2);
            gain2.connect(masterGain);
            osc2.start(now + 0.10);
            osc2.stop(now + 0.95);

            // Harmonico sutil de sino de vidro (C7 - 2093 Hz)
            const osc3 = ctx.createOscillator();
            const gain3 = ctx.createGain();
            osc3.type = 'triangle';
            osc3.frequency.setValueAtTime(2093.00, now + 0.11);
            gain3.gain.setValueAtTime(0.001, now + 0.11);
            gain3.gain.exponentialRampToValueAtTime(0.10, now + 0.13);
            gain3.gain.exponentialRampToValueAtTime(0.0001, now + 0.55);
            osc3.connect(gain3);
            gain3.connect(masterGain);
            osc3.start(now + 0.11);
            osc3.stop(now + 0.60);
        } catch (e) {
            console.warn('Erro ao reproduzir som de oportunidade:', e);
        }
    };

    // Controle de Audio Ativar/Desativar
    window.toggleSoundNotifications = function() {
        getAudioContext();
        soundEnabled = !soundEnabled;
        localStorage.setItem('infecto_sound_enabled', soundEnabled ? 'true' : 'false');
        updateSoundButtonUI();
        if (soundEnabled) {
            window.playVictorySound();
            showInfectoToast('🔊 Efeitos Sonoros Ativados!', 'Sons de Vitoria (Videogame) e Oportunidade (Pendente) habilitados.', 'success');
        } else {
            showInfectoToast('🔇 Efeitos Sonoros Silenciados', 'Notificacoes sonoras pausadas.', 'info');
        }
    };

    window.testVictorySound = function() {
        getAudioContext();
        window.playVictorySound();
        showInfectoToast('🎮 Teste de Vitoria (Videogame)', '🎉 Matricula Confirmada: Dr(a). Aluno Exemplo — Pos-Graduacao', 'success');
    };

    window.testOpportunitySound = function() {
        getAudioContext();
        window.playOpportunitySound();
        showInfectoToast('⚡ Teste de Oportunidade', '⚠️ Matricula Pendente: Lead Exemplo — S.O.S Antibiotico', 'warning');
    };

    function updateSoundButtonUI() {
        const btn = document.getElementById('hud-sound-btn');
        const icon = document.getElementById('sound-icon');
        const text = document.getElementById('sound-text');
        if (!btn) return;
        if (soundEnabled) {
            btn.style.background = 'rgba(234, 179, 8, 0.18)';
            btn.style.borderColor = 'rgba(234, 179, 8, 0.6)';
            btn.style.boxShadow = '0 0 12px rgba(234, 179, 8, 0.25)';
            if (icon) icon.innerText = '🔊';
            if (text) {
                text.style.color = '#fde047';
                text.innerText = 'ÁUDIO: ON';
            }
        } else {
            btn.style.background = 'rgba(100, 116, 139, 0.15)';
            btn.style.borderColor = 'rgba(100, 116, 139, 0.4)';
            btn.style.boxShadow = 'none';
            if (icon) icon.innerText = '🔇';
            if (text) {
                text.style.color = '#94a3b8';
                text.innerText = 'ÁUDIO: MUDO';
            }
        }
    }

    // TOAST NOTIFICATION CONTAINER (Cyberpunk Glassmorphism)
    window.showInfectoToast = function(title, message, type = 'success') {
        let container = document.getElementById('infecto-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'infecto-toast-container';
            container.style.cssText = 'position:fixed; top:24px; right:24px; z-index:999999; display:flex; flex-direction:column; gap:12px; pointer-events:none; max-width:400px; width:calc(100% - 48px);';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.style.cssText = 'pointer-events:auto; background:rgba(10, 15, 26, 0.97); border-radius:10px; padding:14px 18px; box-shadow:0 12px 30px -5px rgba(0,0,0,0.85); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,0.12); color:#fff; font-family:var(--font-sans, system-ui, sans-serif); transform:translateX(120%); opacity:0; transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);';

        if (type === 'success') {
            toast.style.borderLeft = '5px solid #10b981';
            toast.style.boxShadow = '0 12px 30px -5px rgba(0,0,0,0.85), 0 0 25px rgba(16,185,129,0.35)';
        } else if (type === 'warning') {
            toast.style.borderLeft = '5px solid #f59e0b';
            toast.style.boxShadow = '0 12px 30px -5px rgba(0,0,0,0.85), 0 0 25px rgba(245,158,11,0.35)';
        } else if (type === 'info') {
            toast.style.borderLeft = '5px solid #00f0ff';
            toast.style.boxShadow = '0 12px 30px -5px rgba(0,0,0,0.85), 0 0 20px rgba(0,240,255,0.25)';
        }

        toast.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
                <div style="font-weight:800; font-size:13.5px; color:${type === 'warning' ? '#fbbf24' : (type === 'success' ? '#34d399' : '#38bdf8')}; font-family:var(--font-hud, system-ui, sans-serif); letter-spacing:0.03em;">
                    ${title}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="background:none; border:none; color:#94a3b8; font-size:15px; cursor:pointer; padding:0; line-height:1;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#94a3b8'">✕</button>
            </div>
            <div style="font-size:12.5px; color:#e2e8f0; margin-top:5px; line-height:1.45;">
                ${message}
            </div>
        `;

        container.appendChild(toast);
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        });

        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 450);
        }, 7000);
    };

    // DETECCAO AUTOMATICA DE NOVAS MATRICULAS AO CARREGAR / ATUALIZAR
    let lastKnownConfirmedKeys = null;
    let lastKnownPendingKeys = null;

    window.checkForNewEnrollmentEvents = function(currentConfirmadas, currentPendentes) {
        if (!currentConfirmadas || !currentPendentes) return;

        const currentConfKeys = new Set(currentConfirmadas.map(c => (c.email + '|' + c.curso).toLowerCase()));
        const currentPendKeys = new Set(currentPendentes.map(p => (p.email + '|' + p.curso).toLowerCase()));

        // Primeira carga da pagina na sessao: apenas inicializa
        if (lastKnownConfirmedKeys === null || lastKnownPendingKeys === null) {
            lastKnownConfirmedKeys = currentConfKeys;
            lastKnownPendingKeys = currentPendKeys;
            return;
        }

        // Detecta novas matriculas confirmadas (vendas/pagamentos)
        const newConfirmed = currentConfirmadas.filter(c => !lastKnownConfirmedKeys.has((c.email + '|' + c.curso).toLowerCase()));
        if (newConfirmed.length > 0) {
            newConfirmed.forEach((c, idx) => {
                setTimeout(() => {
                    window.playVictorySound();
                    showInfectoToast(
                        '🎉 NOVA MATRÍCULA CONFIRMADA! (Venda)',
                        `<b>${c.nome || 'Novo Aluno'}</b> matriculado em <b>${c.curso}</b> ${c.valor ? '· R$ ' + Number(c.valor).toLocaleString('pt-BR', {minimumFractionDigits:2}) : ''}`,
                        'success'
                    );
                }, idx * 1200);
            });
        }

        // Detecta novas matriculas pendentes (oportunidades comerciais)
        const newPending = currentPendentes.filter(p => !lastKnownPendingKeys.has((p.email + '|' + p.curso).toLowerCase()));
        if (newPending.length > 0) {
            newPending.forEach((p, idx) => {
                setTimeout(() => {
                    window.playOpportunitySound();
                    showInfectoToast(
                        '⚡ NOVA OPORTUNIDADE! (Matrícula Pendente)',
                        `<b>${p.nome || 'Novo Lead'}</b> iniciou inscrição em <b>${p.curso}</b>. Aguardando pagamento!`,
                        'warning'
                    );
                }, idx * 1200);
            });
        }

        lastKnownConfirmedKeys = currentConfKeys;
        lastKnownPendingKeys = currentPendKeys;
    };

    // Auto-polling em background a cada 60s
    function pollLiveDashboardUpdates() {
        fetch('dashboard_gerado.html?_nocache=' + Date.now(), { cache: 'no-store' })
            .then(res => {
                if (!res.ok) throw new Error('Status ' + res.status);
                return res.text();
            })
            .then(html => {
                const pos = html.indexOf('const DATA = {');
                if (pos !== -1) {
                    const endPos = html.indexOf('let CURRENT_DATA', pos);
                    const semicolonPos = html.rfind ? html.rfind(';', pos, endPos + 10) : html.lastIndexOf(';', endPos);
                    const dataStr = html.substring(pos + 'const DATA = '.length, semicolonPos);
                    const newData = JSON.parse(dataStr);
                    
                    if (newData && newData.meta && window.DATA && window.DATA.meta) {
                        if (newData.meta.updated_iso !== window.DATA.meta.updated_iso || newData.meta.updated_at !== window.DATA.meta.updated_at) {
                            console.log('Novos dados detectados automaticamente! Atualizando dashboard...');
                            window.DATA = newData;
                            if (typeof window.applyFilters === 'function') {
                                window.applyFilters();
                            }
                            if (typeof window.getMatriculasAuditoriaData === 'function') {
                                const aud = window.getMatriculasAuditoriaData();
                                window.checkForNewEnrollmentEvents(aud.allRecords, aud.allPendentes);
                            }
                        }
                    }
                }
            })
            .catch(() => {});
    }

    document.addEventListener('DOMContentLoaded', () => {
        updateSoundButtonUI();
        setTimeout(() => {
            if (typeof window.getMatriculasAuditoriaData === 'function') {
                const aud = window.getMatriculasAuditoriaData();
                window.checkForNewEnrollmentEvents(aud.allRecords, aud.allPendentes);
            }
        }, 1000);
        setInterval(pollLiveDashboardUpdates, 60000);
    });
})();
</script>
'''

    if 'id="infecto-toast-container"' not in html and 'window.playVictorySound' not in html:
        # Inserir antes de </body>
        idx_body_close = html.rfind('</body>')
        if idx_body_close != -1:
            html = html[:idx_body_close] + audio_system_js + '\n' + html[idx_body_close:]
        else:
            html = html + '\n' + audio_system_js
        print("[OK] Sistema de Audio e Notificacoes inserido no final do template!")
    else:
        print("[INFO] Sistema de audio ja inserido.")

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("[OK] template.html salvo com sucesso!")
    return True

if __name__ == '__main__':
    apply_audio_patch()
