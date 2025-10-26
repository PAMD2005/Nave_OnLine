# 🚀 Nave OnLine

**Nave OnLine** é um jogo arcade desenvolvido em **Python** usando **Tkinter**.  
O jogador controla uma nave espacial usando as teclas **WASD**, navegando pelo espaço para capturar planetas e avançar pelos níveis.

## 🕹️ Como Jogar
- Use as teclas **W**, **A**, **S**, **D** para mover a nave.  
- Capture planetas para avançar de nível.  
- No estágio final, sobreviva à **chuva de meteoros** pelo maior tempo possível.

## ✨ Funcionalidades
- Construído inteiramente com **Python** e **Tkinter**.  
- Controles suaves com WASD.  
- Dificuldade progressiva: planetas crescem e se movem mais rápido a cada nível.  
- Estágio final de sobrevivência com meteoros.  
- **Nomes de planetas gerados dinamicamente usando uma API de exoplanetas**, proporcionando diversidade e autenticidade no jogo.  

## ⚙️ Sobre a API de Planetas
O jogo usa uma API pública de exoplanetas para gerar nomes únicos para os planetas:

```python
# Obtem os nomes de exoplanetas da API
try:
    req = urllib.request.Request(EXOPLANET_API, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        dados = json.load(resp)
    self.nomes_exo = list({item["pl_name"] for item in dados})
except:
    # Lista reserva caso a API falhe
    self.nomes_exo = ["Kepler-22b", "Proxima Centauri b", "TRAPPIST-1e", "HD 209458 b"]
