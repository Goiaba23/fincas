# FINCAS — Design Brief Completo para UI/UX

## Enviar para: IA de Design (Midjourney / Galileo AI / v0 / Claude Design)

---

## 1. VISÃO GERAL DO PRODUTO

**Nome:** Fincas
**Slogan:** "Sabedoria financeira global em um só lugar"
**Modelo:** SaaS Premium — R$ 40/mês (trial grátis de 7 dias)
**Público-alvo:** Brasileiros de 25-50 anos que querem organizar as finanças pessoais

**O diferencial:** Não é mais um app de orçamento genérico. O Fincas reúne **8 métodos financeiros comprovados de 5 países** (Japão, Suécia, Holanda, Suíça, Brasil) em uma única plataforma. Cada método tem décadas ou séculos de uso real.

**Tom de voz:** Confiável, acolhedor, aspiracional. Mistura dados frios com sabedoria cultural. "Seu dinheiro merece sabedoria global."

**Paleta de cores:**
- **Primária:** Verde financeiro (#16A34A / hsl(142, 76%, 36%)) — remete a crescimento, saúde financeira, natureza
- **Fundo:** Cinza claro suave (#F8FAFC) — clean, profissional
- **Cards:** Branco com sombras suaves
- **Acentos:** Cada método financeiro tem sua própria cor gradiente (veja seção 5)
- **Modo escuro:** Tons escuros (#0A0A0F) com verde mais claro como primário

**Tipografia:** Inter (sans-serif) — moderna, legível, brasileira-friendly

**Ícones:** Lucide React — estilo outline, 5px stroke, consistentes

---

## 2. DESIGN SYSTEM — COMPONENTES GLOBAIS

### 2.1 Sidebar (Navegação Principal)
- **Posição:** Fixed à esquerda, altura total da tela
- **Estado:** Colapsável (64px fechado / 256px aberto)
- **Aberto:** Mostra logo "Fincas" no topo + todos os links com texto + ícone
- **Fechado:** Mostra apenas ícones
- **Links (11 no total):**
  - Dashboard (ícone: LayoutDashboard)
  - Transações (ícone: ArrowRightLeft)
  - Métodos Financeiros (ícone: Globe) — **destacado como principal**
  - Kakeibo (ícone: BookOpen)
  - Micro-Poupança (ícone: TrendingDown)
  - Mais Métodos (ícone: Globe)
  - Planos (ícone: CreditCard) — **com badge "Trial" ou "Premium"**
  - Orçamentos (ícone: PiggyBank)
  - Metas (ícone: Target)
  - Assistente IA (ícone: Bot)
  - Configurações (ícone: Settings)
- **Footer:** Nome do usuário + botão Sair
- **Transição:** Animação suave de 200ms, expandindo/colapsando

### 2.2 Trial Banner
- **Posição:** Topo do conteúdo principal (abaixo do header da sidebar)
- **Estados:**
  - Trial ativo: Fundo verde claro, ícone Sparkles, texto "🎯 Trial grátis — X dias restantes", botão "Ver planos"
  - Expirado: Fundo vermelho claro, ícone AlertTriangle, texto "⏰ Trial expirado — renove", botão "Renovar"
  - Nenhum: Fundo azul claro, "📋 Ative seu trial grátis de 7 dias", botão "Ver planos"
- **Ação:** Botão "X" para dispensar, botão CTA para ir à página de planos

### 2.3 Cards (Padrão shadcn/ui)
- Border-radius: 12px (0.75rem)
- Sombra suave (shadow-sm)
- Padding interno: 24px
- Cabeçalho com título + descrição opcional
- Gradientes de fundo para cards especiais

### 2.4 Botões
- **Primary:** Fundo verde, texto branco, sem sombra
- **Outline:** Borda, fundo transparente
- **Ghost:** Sem borda, sem fundo

---

## 3. PÁGINA DE LOGIN (/login)

**Propósito:** Cadastro e autenticação

**Layout:** Tela cheia, sem sidebar, sem header
- 50% esquerda: Ilustração grande aspiracional — mapa mundi estilizado com bandeiras dos 5 países (Japão, Suécia, Holanda, Suíça, Brasil) conectados por linhas douradas, representando a "sabedoria financeira global"
- 50% direita: Card de formulário centralizado verticalmente
  - Logo "Fincas" no topo
  - Título: "Sua jornada financeira global começa aqui"
  - Subtítulo: "8 métodos de 5 países para transformar sua relação com o dinheiro"
  - Abas/toggle: "Entrar" | "Cadastrar"
  - Formulário: Email, Senha, Nome (só no cadastro)
  - Botão: "Começar" (verde, cheio)
  - Texto: "Grátis por 7 dias • R$ 40/mês depois"
- **Modo escuro:** Mesmo layout, fundo escuro, ilustração adaptada

---

## 4. DASHBOARD (/)

**Propósito:** Visão geral financeira do usuário

**Layout:** Grid responsivo

### 4.1 Header
- Saudação personalizada: "Olá, [nome] ☀️" (com variação conforme horário)
- Botão "Check-in Kakeibo" (se não feito hoje)
- Indicador de assinatura no canto superior direito

### 4.2 Stat Cards (4 cards em grid)
- **Saldo Atual:** Ícone Wallet, fundo azul claro
- **Receitas do Mês:** Ícone TrendingUp, fundo verde claro
- **Despesas do Mês:** Ícone TrendingDown, fundo vermelho claro
- **Transações:** Ícone DollarSign, fundo roxo claro
- Formato: ícone redondo à esquerda, valor grande em negrito, rótulo pequeno

### 4.3 Métodos em Destaque (horizontal scroll)
- 4 mini-cards lado a lado com os métodos mais ativos
- Cada card: bandeira + nome do método + benefício
- Rolagem horizontal em mobile

### 4.4 Últimas Transações (card cheio)
- Tabela/listagem das 10 últimas transações
- Cada linha: ícone seta verde/vermelha, descrição, data, valor
- Link "Ver todas" no final

### 4.5 Trial Banner (se aplicável)
- Conforme seção 2.2

---

## 5. HUB DE MÉTODOS FINANCEIROS (/fincas)

**Propósito:** Landing page principal do produto — JUSTIFICA OS R$ 40/mês

**Layout:** Grid de 4 colunas (desktop) / 2 colunas (tablet) / 1 coluna (mobile)

### 5.1 Header
- Título: "Métodos Financeiros"
- Subtítulo: "Seu dinheiro merece sabedoria global — 8 métodos de 5 países"
- Badge "Ativo" com ícone Sparkles

### 5.2 Cards dos 8 Métodos (grid principal)

Cada card é um **botão** que leva à página do método. Design consistente:

| Método | Gradiente | Bandeira | Ícone | Benefício |
|--------|-----------|----------|-------|-----------|
| Kakeibo | rose → pink | 🇯🇵 | PiggyBank | Reduz gastos 25-35% |
| Tsumitate | emerald → teal | 🇯🇵 | TrendingDown | Poupe sem perceber |
| Lagom | blue → cyan | 🇸🇪 | Target | Não sobra nem falta |
| Regra 10 | orange → amber | 🇳🇱 | ShieldCheck | 85% poupam |
| Desafio Suíço | red → rose | 🇨🇭 | Flame | Economize R$8.000+ |
| Acordo a Dois | violet → purple | 🇳🇱 | HeartHandshake | 0 brigas |
| Limpeza | slate → gray | 🇸🇪 | Scissors | Economia R$2.400/ano |
| Envelopes | green → lime | 🇧🇷 | Globe | Cada real tem propósito |

**Layout de cada card:**
- Topo: Ícone com gradiente (rounded-lg) + bandeira no canto
- Meio: Nome do país (ex: "Japão"), subtítulo em 2 linhas
- Footer: Badge de benefício (ex: "Reduz gastos 25-35%") + seta que aparece no hover
- Efeito hover: Sobe 2px, sombra aumenta, seta aparece

### 5.3 Seção "Seu progresso global"
- Card com grid 4 colunas
- Atalhos compactos para os métodos mais usados
- Cada atalho: gradiente pequeno + bandeira + nome + benefício

---

## 6. KAKEIBO (/fincas/kakeibo)

**Propósito:** Método japonês de 120 anos — controle financeiro através de 4 perguntas semanais

**Layout:** Duas telas (dashboard + check-in)

### 6.1 Tela Principal (Dashboard)
- **Header:**
  - Título "Kakeibo" + bandeira Japão
  - Subtítulo explicativo
  - Botão "Check-in Semanal" (verde, destaque)

- **Cards de Status (grid 4 colunas):**
  - Card 1 (maior destaque): **Streak semanal** — ícone Flame laranja, número grande (ex: "5"), texto "semanas seguidas", mensagem "🔥 Streak ativo!"
  - Cards 2-5: As 4 categorias Kakeibo:
    - 🏠 Essencial (azul) — Moradia, alimentação, transporte
    - 🎮 Desejos (rosa) — Lazer, restaurantes, hobbies
    - 📚 Cultura (roxo) — Cursos, livros, eventos
    - ⚠️ Imprevistos (âmbar) — Emergências, multas
  - Cada card: emoji grande, valor em R$, descrição curta

- **Resumo da Semana (card cheio):**
  - Receitas vs Despesas (lado a lado)
  - Taxa de Poupança com barra de progresso colorida
  - Comparativo com média histórica

- **Callout Educativo:**
  - Fundo âmbar claro
  - Ícone HelpCircle
  - Explicação dos 4 pilares do Kakeibo
  - "O segredo não é cortar tudo, mas equilibrar"

### 6.2 Tela de Check-in (modal/página separada)
- **Layout:** Largura máxima 600px, centralizado

- **Pergunta 1 — Poupança (card com 2 inputs lado a lado):**
  - "Quanto você conseguiu poupar esta semana?" (input R$)
  - "Quanto você queria ter poupado?" (input R$)
  - Dica abaixo de cada input

- **Pergunta 2 — Reflexão (card com 2 textareas):**
  - "O que deu certo?" (textarea, placeholder: "Um gasto que valeu a pena...")
  - "O que pode melhorar?" (textarea, placeholder: "Um gasto desnecessário...")

- **Botão de envio:** "Concluir Check-in Semanal" (verde, largura total)

- **Tela de sucesso:** Ícone CheckCircle2 verde, mensagem "Check-in registrado!", botão "Ver relatório"

---

## 7. MICRO-POUPANÇA (/fincas/micro-savings)

**Propósito:** Poupança automática estilo Acorns + Tsumitate japonês

**Layout:** Página única com seções

### 7.1 Header
- Título "Micro-Poupança" + bandeira 🇯🇵
- Subtítulo "Poupe sem perceber"
- Botão "Nova Regra" (verde, outline ou cheio)

### 7.2 Cards de Métricas (grid 3 colunas)
- **Regras Ativas:** Ícone Coins verde, número grande
- **Acumulado no Mês:** Ícone ArrowDownToLine azul, valor em R$
- **Próximo Round-up:** Ícone Timer âmbar, descrição "Automático"

### 7.3 Formulário "Nova Regra" (collapse)
- **Nome:** Input "Ex: Arredondar mercado"
- **Tipo:** Select (Round-up / Valor Fixo / Percentual da Receita)
- **Frequência:** Select (Diária / Semanal / Mensal)
- **Valor/Percentual:** Input numérico
- **Meta opcional:** Input "R$ 0,00 = sem limite"
- **Botão:** "Criar Regra Automática"

### 7.4 Lista de Regras (card cheio)
- Cada regra: ícone Zap verde, nome, descrição do tipo, valor economizado no mês
- Botões: "Executar" (outline) + "Excluir" (ícone lixeira vermelho)
- Estado vazio: ilustração TrendingDown + "Nenhuma regra ainda"

---

## 8. GASTÔMETRO LAGOM (/fincas/lagom)

**Propósito:** Burndown orçamentário sueco — "nem demais, nem de menos"

### 8.1 Header
- Título "Gastômetro Lagom" + bandeira 🇸🇪
- Explicação do conceito Lagom

### 8.2 Seletor de Mês
- Input tipo "month"
- Label "Mês:" ao lado

### 8.3 Card Principal — Zona de Burndown
- **Background:** Verde (seguro) / Amarelo (atenção) / Vermelho (perigo) conforme progresso
- **Topo:** Label da zona + badge indicador
- **Barra de progresso:** Largura total, cor conforme zona
- **Métricas (grid 4 colunas):**
  - Orçamento total
  - Gasto até agora (vermelho)
  - Restante (verde se positivo, vermelho se negativo)
  - Ritmo diário ideal (R$/dia)

### 8.4 Cards Inferiores (grid 2 colunas)
- **Burndown Ideal vs Real:**
  - Barra azul (ideal linear)
  - Barra verde/vermelha (real)
  - Mensagem: "Dentro do esperado" ou "X acima do ideal"
- **Como funciona o Lagom:**
  - Explicação do conceito sueco
  - 3 zonas explicadas

---

## 9. MAIS MÉTODOS (/fincas/metodos)

**Propósito:** Vitrine dos 5 métodos complementares

**Layout:** Grid 2 colunas (desktop)

### 9.1 Cards Individuais (cada um com gradiente único)

**🇳🇱 Regra 10 — Pay Yourself First**
- Background: laranja/âmbar
- Explicação: "10% automático antes de qualquer gasto"
- 3 cards menores: "10%", "Automático", "Aposentadoria"
- Call to action: "Configure na aba Micro-Poupança"

**🇨🇭 Desafio Suíço**
- Background: vermelho/rosa
- **Streak:** Número grande de meses + ícone Flame
- **Juros evitados:** Valor em verde
- **Histórico:** Últimos 6 meses com check verde/vermelho
- **Estado vazio:** "Nenhum cartão importado"

**🇳🇱 Acordo a Dois — Polder Model**
- Background: violeta/roxo
- Explicação do modelo holandês de consenso
- 3 modelos: Merged (tudo junto), Separado, Híbrido (proporcional)
- "Em breve: gestão compartilhada"

**🇸🇪 Limpeza Financeira — Döstädning**
- Background: slate/cinza
- **Total de assinaturas:** Número grande
- **Lista:** Até 5 assinaturas com status (usada/não usada)
- **Desperdício anual:** Card vermelho com valor
- **Estado vazio:** "Importe transações para detectar"

**🇧🇷 Envelopes Pix — Caixinhas 2.0**
- Background: verde/lime
- Inspiração: YNAB + Nubank
- 2 conceitos: Zero-sum + Rollover
- "Em breve"

### 9.2 Mapa dos Métodos (card footer)
- Grid 5 colunas
- Cada coluna: bandeira grande + nome do(s) método(s) + país

---

## 10. PLANOS E ASSINATURA (/planos)

**Propósito:** Conversão — mostrar valor e ativar trial/pagamento

### 10.1 Status Atual (banner)
- Trial ativo: verde, "🎯 Trial — X dias", botão "Assinar"
- Expirado: vermelho, "⏰ Expirado", botão "Renovar"
- Ativo: verde, "✅ Plano ativo"

### 10.2 Cards de Planos (grid 2 colunas)

**Card 1 — Trial 7 Dias**
- Badge "Trial grátis" no canto
- Preço: "Grátis" + "por 7 dias"
- 6 features listadas (CheckCircle2 verde)
- Botão: "Ativar Trial Grátis" (outline) — desabilitado se já ativo

**Card 2 — Fincas Premium (DESTAQUE)**
- Badge "Recomendado" no canto, borda verde destacada
- Preço: "R$ 40" + "/mês" + "Menos de R$ 1,40 por dia"
- **TODAS as 12 features listadas**
- Botão: "Assinar Agora" (verde cheio) — desabilitado se já ativo

### 10.3 Card "Por que R$ 40/mês?"
- Ícone Globe
- 4 parágrafos explicando o valor:
  - 8 métodos de 5 países
  - Assistente IA
  - Sync bancário
  - Menos de R$ 1,40/dia

### 10.4 Cancelamento (seção recolhida)
- Link "Cancelar assinatura" (texto cinza)
- Ao clicar: Card vermelho de confirmação
- Botões: "Continuar assinatura" (outline) + "Sim, cancelar" (destrutivo)

---

## 11. DEMAIS PÁGINAS (sidebar referenciado)

### 11.1 Transações (/transactions)
- Lista completa com ícones de entrada/saída
- Cores: verde (depósito), vermelho (retirada)
- Formato: ícone + descrição + data + valor

### 11.2 Orçamentos (/budgets) — *a construir*
### 11.3 Metas (/goals) — *a construir*
### 11.4 Assistente IA (/assistant) — *a construir*
### 11.5 Configurações (/settings) — *a construir*

---

## 12. DARK MODE

- **Background:** hsl(240, 10%, 3.9%) — quase preto
- **Cards:** hsl(240, 10%, 5.9%) — levemente mais claro
- **Texto:** hsl(0, 0%, 98%) — quase branco
- **Primary:** hsl(142, 70%, 45%) — verde mais vibrante que no light
- **Bordas:** hsl(240, 3.7%, 15.9%)
- **Gradientes dos cards de método:** versões mais escuras e suaves (ex: from-rose-950/20)
- **Toggle:** Botão Lua/Sol no header ou config
- **Transição:** Suave entre modos (0.3s)

---

## 13. RESPONSIVIDADE

| Breakpoint | Layout |
|------------|--------|
| > 1024px | Desktop completo: sidebar expandida + grid 4 colunas |
| 768-1024px | Tablet: sidebar colapsada + grid 2-3 colunas |
| < 768px | Mobile: sidebar como drawer/overlay + grid 1 coluna |
| < 480px | Mobile pequeno: fontes reduzidas, padding menor |

- Sidebar vira drawer em mobile (botão hamburguer)
- TrialBanner vira alerta empilhável em mobile
- Cards de método viram scroll horizontal em mobile
- Tabelas viram listas em mobile

---

## 14. ANIMAÇÕES E MICRO-INTERAÇÕES

- **Sidebar collapse/expand:** 200ms ease
- **Card hover:** translateY(-2px), shadow-lg, 200ms
- **Streak counter:** Número "pula" ao aumentar
- **Gradientes:** Animação sutil de movimento (se possível)
- **Loading states:** Spinner circular verde
- **Empty states:** Ilustração + texto + CTA
- **Transições de página:** Fade suave
- **Toast/notificações:** Slide-in do canto superior direito

---

## 15. FLUXOS DE USUÁRIO

### Fluxo 1: Novo usuário (Trial)
```
Registra → Login → Trial Banner "🎯 7 dias" 
        → Dashboard → Vê métodos → Clica Kakeibo
        → Faz check-in semanal → Vê streak
        → Recebe notificação "3 dias restantes"
        → Vai em Planos → Assina R$ 40/mês
```

### Fluxo 2: Usuário pagante
```
Login → Dashboard → Sem banner
     → Usa todos os métodos livremente
     → Configura micro-poupança automática
     → Acompanha Lagom no fim do mês
     → Paga R$ 40/mês todo dia 15
```

### Fluxo 3: Trial expirado
```
Login → Banner vermelho "⚠️ Expirado"
     → Tenta acessar Kakeibo → Bloqueado
     → Clica "Renovar" → Planos → Assina
```

---

## 16. INSTRUÇÕES PARA IA DE DESIGN

"Projete um SaaS financeiro chamado **Fincas** — uma plataforma que reúne 8 métodos financeiros de 5 países (Japão, Suécia, Holanda, Suíça, Brasil). O público é brasileiro de 25-50 anos. O tom é confiável, acolhedor e aspiracional. A paleta é verde como cor principal (#16A34A), com fundo cinza claro (#F8FAFC). Cada método financeiro tem sua própria cor gradiente. A tipografia é Inter. O layout tem sidebar esquerda colapsável com ícones Lucide. O design precisa ser limpo, moderno, com cards de bordas arredondadas (12px) e sombras suaves. Priorize a clareza das informações e a hierarquia visual. O dashboard principal deve comunicar: '8 métodos de 5 países transformando sua relação com o dinheiro'. Crie variações para desktop, tablet e mobile. Inclua dark mode."

---

## 17. REFERÊNCIAS VISUAIS

- **Linear.app** — sidebar colapsável, design limpo
- **Notion** — hierarquia de blocos, tipografia limpa
- **YNAB** — conceito de orçamento, cores financeiras
- **Nubank** — design brasileiro, roxinho + simplicidade
- **Acorns** — micro-investimento, verde, round-ups
- **Duolingo** — streaks, gamificação, consistência
- **Linear + Vercel** — dark mode de qualidade
