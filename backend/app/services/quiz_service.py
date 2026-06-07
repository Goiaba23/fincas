QUIZ_QUESTIONS = [
    {
        "id": "age",
        "question": "Qual sua faixa etária?",
        "type": "multiple_choice",
        "options": [
            {"value": "under_18", "label": "Menos de 18 anos"},
            {"value": "18_25", "label": "18-25 anos"},
            {"value": "26_35", "label": "26-35 anos"},
            {"value": "36_50", "label": "36-50 anos"},
            {"value": "over_50", "label": "Mais de 50 anos"},
        ],
    },
    {
        "id": "monthly_income",
        "question": "Qual sua renda mensal aproximada?",
        "type": "multiple_choice",
        "options": [
            {"value": "up_to_1k", "label": "Até R$ 1.000"},
            {"value": "1k_3k", "label": "R$ 1.000 - R$ 3.000"},
            {"value": "3k_7k", "label": "R$ 3.000 - R$ 7.000"},
            {"value": "7k_15k", "label": "R$ 7.000 - R$ 15.000"},
            {"value": "over_15k", "label": "Mais de R$ 15.000"},
        ],
    },
    {
        "id": "income_stability",
        "question": "Como é sua renda?",
        "type": "multiple_choice",
        "options": [
            {"value": "fixed", "label": "Fixa (CLT, servidor público)"},
            {"value": "variable", "label": "Variável (freelancer, comissão)"},
            {"value": "mixed", "label": "Mista (fixo + variável)"},
            {"value": "uncertain", "label": "Incerta (bicos, informal)"},
        ],
    },
    {
        "id": "savings_discipline",
        "question": "Como você descreveria seu hábito de poupar?",
        "type": "likert",
        "options": [
            {"value": 1, "label": "Nunca sobra nada no fim do mês"},
            {"value": 2, "label": "Poupo raramente"},
            {"value": 3, "label": "Poupo quando sobra"},
            {"value": 4, "label": "Tento poupar todo mês"},
            {"value": 5, "label": "Poupo religiosamente todo mês"},
        ],
    },
    {
        "id": "spending_personality",
        "question": "Qual frase mais combina com você?",
        "type": "multiple_choice",
        "options": [
            {"value": "impulsive", "label": "Compro por impulso, depois vejo o estrago"},
            {"value": "planned", "label": "Planejo cada gasto com antecedência"},
            {"value": "balanced", "label": "Tenho meus momentos, mas no geral me controlo"},
            {"value": "frugal", "label": "Penso 3x antes de comprar qualquer coisa"},
        ],
    },
    {
        "id": "financial_literacy",
        "question": "Qual seu nível de conhecimento financeiro?",
        "type": "multiple_choice",
        "options": [
            {"value": "beginner", "label": "Iniciante — nunca fiz orçamento"},
            {"value": "basic", "label": "Básico — sei o que ganho e gasto"},
            {"value": "intermediate", "label": "Intermediário — já usei planilhas ou apps"},
            {"value": "advanced", "label": "Avançado — invisto e controlo tudo"},
        ],
    },
    {
        "id": "goal_type",
        "question": "Qual seu principal objetivo financeiro agora?",
        "type": "multiple_choice",
        "options": [
            {"value": "emergency_fund", "label": "Criar reserva de emergência"},
            {"value": "pay_debt", "label": "Sair das dívidas"},
            {"value": "dream", "label": "Realizar um sonho (viagem, carro, casa)"},
            {"value": "invest", "label": "Começar a investir"},
            {"value": "control", "label": "Ter controle sobre meus gastos"},
            {"value": "subscriptions", "label": "Reduzir assinaturas e gastos fixos"},
        ],
    },
    {
        "id": "credit_card_use",
        "question": "Como você usa o cartão de crédito?",
        "type": "multiple_choice",
        "options": [
            {"value": "no_card", "label": "Não tenho cartão de crédito"},
            {"value": "full_payment", "label": "Pago integralmente todo mês"},
            {"value": "partial", "label": "Às vezes pago parcialmente"},
            {"value": "revolving", "label": "Frequentemente pago só o mínimo"},
            {"value": "multiple", "label": "Tenho vários cartões e misturo as faturas"},
        ],
    },
    {
        "id": "household",
        "question": "Qual sua situação de moradia?",
        "type": "multiple_choice",
        "options": [
            {"value": "single", "label": "Moro sozinho(a)"},
            {"value": "couple", "label": "Moro com parceiro(a)"},
            {"value": "family", "label": "Moro com família (filhos, pais)"},
            {"value": "roommates", "label": "Divido casa/apartamento"},
        ],
    },
    {
        "id": "subscription_count",
        "question": "Quantas assinaturas você tem? (streaming, apps, academias...)",
        "type": "multiple_choice",
        "options": [
            {"value": "none", "label": "Nenhuma"},
            {"value": "1_3", "label": "1-3 assinaturas"},
            {"value": "4_6", "label": "4-6 assinaturas"},
            {"value": "7_plus", "label": "7 ou mais assinaturas"},
        ],
    },
    {
        "id": "savings_goal_dream",
        "question": "Pense em um sonho que você quer realizar com dinheiro. Como descreveria?",
        "type": "text",
        "placeholder": "Ex: Viajar para o Japão em 2027, Comprar meu primeiro carro, Dar entrada num apartamento...",
    },
]

METHOD_PROFILES = {
    "kakeibo": {
        "name": "Kakeibo",
        "origin": "Japão",
        "icon": "book-open",
        "tagline": "4 perguntas que transformam sua relação com o dinheiro",
        "description": "Método japonês centenário baseado em mindfulness financeiro. Responda 4 perguntas toda semana e reduza gastos em 25-35% naturalmente.",
        "benefits": ["Reduz gastos supérfluos", "Aumenta consciência financeira", "Cria hábito de reflexão semanal"],
        "best_for": "Quem quer desenvolver uma relação mais consciente com o dinheiro e está aberto à introspecção.",
        "scores": {
            "age": {"under_18": 2, "18_25": 4, "26_35": 3, "36_50": 3, "over_50": 4},
            "monthly_income": {"up_to_1k": 4, "1k_3k": 4, "3k_7k": 3, "7k_15k": 2, "over_15k": 2},
            "income_stability": {"fixed": 3, "variable": 4, "mixed": 3, "uncertain": 3},
            "savings_discipline": {1: 4, 2: 4, 3: 3, 4: 2, 5: 1},
            "spending_personality": {"impulsive": 5, "planned": 1, "balanced": 3, "frugal": 1},
            "financial_literacy": {"beginner": 5, "basic": 4, "intermediate": 2, "advanced": 1},
            "goal_type": {"emergency_fund": 2, "pay_debt": 2, "dream": 4, "invest": 1, "control": 5, "subscriptions": 2},
            "credit_card_use": {"no_card": 3, "full_payment": 2, "partial": 4, "revolving": 5, "multiple": 4},
            "household": {"single": 4, "couple": 2, "family": 2, "roommates": 3},
            "subscription_count": {"none": 4, "1_3": 3, "4_6": 2, "7_plus": 1},
        },
    },
    "tsumitate": {
        "name": "Tsumitate",
        "origin": "Japão",
        "icon": "trending-down",
        "tagline": "Micro-poupança automática que você nem sente",
        "description": "Inspirado no Tsumitate NISA japonês e Acorns. Pequenas quantias todo dia/semana constroem uma poupança sem esforço.",
        "benefits": ["Poupa sem esforço", "Consistência sobre quantidade", "Round-up de compras vira poupança"],
        "best_for": "Quem tem dificuldade de poupar mas quer começar com algo automático e sem dor.",
        "scores": {
            "age": {"under_18": 4, "18_25": 5, "26_35": 4, "36_50": 2, "over_50": 1},
            "monthly_income": {"up_to_1k": 5, "1k_3k": 5, "3k_7k": 4, "7k_15k": 2, "over_15k": 1},
            "income_stability": {"fixed": 4, "variable": 3, "mixed": 3, "uncertain": 2},
            "savings_discipline": {1: 5, 2: 5, 3: 3, 4: 2, 5: 1},
            "spending_personality": {"impulsive": 4, "planned": 2, "balanced": 3, "frugal": 1},
            "financial_literacy": {"beginner": 5, "basic": 4, "intermediate": 3, "advanced": 1},
            "goal_type": {"emergency_fund": 5, "pay_debt": 3, "dream": 4, "invest": 2, "control": 2, "subscriptions": 1},
            "credit_card_use": {"no_card": 3, "full_payment": 4, "partial": 3, "revolving": 2, "multiple": 2},
            "household": {"single": 4, "couple": 3, "family": 3, "roommates": 4},
            "subscription_count": {"none": 3, "1_3": 4, "4_6": 3, "7_plus": 2},
        },
    },
    "regra_10": {
        "name": "Regra 10",
        "origin": "Holanda",
        "icon": "percent",
        "tagline": "10% de tudo que você ganha é seu — o resto é dos outros",
        "description": "O método holandês mais simples: separe 10% de toda entrada antes de qualquer gasto. 85% dos holandeses poupam assim.",
        "benefits": ["Cria reserva automaticamente", "Não depende de sobra", "Pague-se primeiro"],
        "best_for": "Iniciantes que querem a regra mais simples e eficaz para começar a poupar.",
        "scores": {
            "age": {"under_18": 3, "18_25": 5, "26_35": 4, "36_50": 4, "over_50": 3},
            "monthly_income": {"up_to_1k": 4, "1k_3k": 5, "3k_7k": 4, "7k_15k": 3, "over_15k": 2},
            "income_stability": {"fixed": 5, "variable": 3, "mixed": 4, "uncertain": 2},
            "savings_discipline": {1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
            "spending_personality": {"impulsive": 5, "planned": 2, "balanced": 3, "frugal": 1},
            "financial_literacy": {"beginner": 5, "basic": 4, "intermediate": 2, "advanced": 1},
            "goal_type": {"emergency_fund": 5, "pay_debt": 3, "dream": 4, "invest": 2, "control": 3, "subscriptions": 1},
            "credit_card_use": {"no_card": 3, "full_payment": 4, "partial": 3, "revolving": 2, "multiple": 2},
            "household": {"single": 4, "couple": 3, "family": 3, "roommates": 4},
            "subscription_count": {"none": 3, "1_3": 3, "4_6": 3, "7_plus": 3},
        },
    },
    "lagom": {
        "name": "Gastômetro Lagom",
        "origin": "Suécia",
        "icon": "target",
        "tagline": "Nem demais, nem de menos — o equilíbrio sueco",
        "description": "O Lagom sueco aplicado ao orçamento. Um burndown chart mostra seu ritmo de gastos: verde (até 85%), amarelo (85-100%), vermelho (>100%).",
        "benefits": ["Evita exageros", "Visualização clara do ritmo", "Comparação com sua média histórica"],
        "best_for": "Quem já tem algum controle mas quer monitoramento visual para não perder o rumo.",
        "scores": {
            "age": {"under_18": 1, "18_25": 3, "26_35": 4, "36_50": 5, "over_50": 5},
            "monthly_income": {"up_to_1k": 2, "1k_3k": 3, "3k_7k": 4, "7k_15k": 4, "over_15k": 3},
            "income_stability": {"fixed": 5, "variable": 3, "mixed": 4, "uncertain": 2},
            "savings_discipline": {1: 2, 2: 3, 3: 5, 4: 4, 5: 2},
            "spending_personality": {"impulsive": 2, "planned": 4, "balanced": 5, "frugal": 2},
            "financial_literacy": {"beginner": 1, "basic": 3, "intermediate": 5, "advanced": 4},
            "goal_type": {"emergency_fund": 3, "pay_debt": 2, "dream": 3, "invest": 3, "control": 4, "subscriptions": 2},
            "credit_card_use": {"no_card": 2, "full_payment": 5, "partial": 4, "revolving": 2, "multiple": 3},
            "household": {"single": 3, "couple": 4, "family": 5, "roommates": 3},
            "subscription_count": {"none": 2, "1_3": 4, "4_6": 5, "7_plus": 4},
        },
    },
    "desafio_suico": {
        "name": "Desafio Suíço",
        "origin": "Suíça",
        "icon": "flame",
        "tagline": "Streak de faturas pagas integralmente — estilo Duolingo",
        "description": "Pague 100% da fatura do cartão todo mês. Streak tracking para motivação. Juros evitados são calculados e exibidos como recompensa.",
        "benefits": ["Zero juros rotativo (14% ao mês no BR)", "Disciplina financeira", "Score de crédito limpo"],
        "best_for": "Usuários de cartão de crédito que querem eliminar o rotativo e criar um streak motivacional.",
        "scores": {
            "age": {"under_18": 1, "18_25": 3, "26_35": 4, "36_50": 4, "over_50": 3},
            "monthly_income": {"up_to_1k": 2, "1k_3k": 3, "3k_7k": 4, "7k_15k": 4, "over_15k": 3},
            "income_stability": {"fixed": 4, "variable": 2, "mixed": 3, "uncertain": 1},
            "savings_discipline": {1: 3, 2: 3, 3: 4, 4: 4, 5: 3},
            "spending_personality": {"impulsive": 3, "planned": 4, "balanced": 3, "frugal": 2},
            "financial_literacy": {"beginner": 2, "basic": 3, "intermediate": 4, "advanced": 3},
            "goal_type": {"emergency_fund": 2, "pay_debt": 5, "dream": 2, "invest": 1, "control": 3, "subscriptions": 1},
            "credit_card_use": {"no_card": 0, "full_payment": 3, "partial": 5, "revolving": 5, "multiple": 4},
            "household": {"single": 3, "couple": 4, "family": 4, "roommates": 3},
            "subscription_count": {"none": 2, "1_3": 3, "4_6": 4, "7_plus": 5},
        },
    },
    "acordo_dois": {
        "name": "Acordo a Dois",
        "origin": "Holanda",
        "icon": "handshake",
        "tagline": "Orçamento do casal sem brigas — modelo Polder holandês",
        "description": "O modelo de consenso holandês aplicado às finanças do casal. 3 modelos (conjunto/separado/híbrido) com regras claras de aprovação.",
        "benefits": ["Evita brigas por dinheiro", "Transparência total", "Metas conjuntas"],
        "best_for": "Casais que querem organizar as finanças juntos com diálogo e consenso.",
        "scores": {
            "age": {"under_18": 1, "18_25": 2, "26_35": 5, "36_50": 5, "over_50": 4},
            "monthly_income": {"up_to_1k": 2, "1k_3k": 3, "3k_7k": 4, "7k_15k": 4, "over_15k": 3},
            "income_stability": {"fixed": 4, "variable": 3, "mixed": 4, "uncertain": 2},
            "savings_discipline": {1: 2, 2: 3, 3: 4, 4: 3, 5: 3},
            "spending_personality": {"impulsive": 3, "planned": 4, "balanced": 3, "frugal": 2},
            "financial_literacy": {"beginner": 3, "basic": 3, "intermediate": 4, "advanced": 3},
            "goal_type": {"emergency_fund": 3, "pay_debt": 3, "dream": 4, "invest": 3, "control": 4, "subscriptions": 2},
            "credit_card_use": {"no_card": 2, "full_payment": 4, "partial": 3, "revolving": 2, "multiple": 3},
            "household": {"single": 0, "couple": 5, "family": 3, "roommates": 1},
            "subscription_count": {"none": 2, "1_3": 4, "4_6": 4, "7_plus": 3},
        },
    },
    "limpeza_financeira": {
        "name": "Limpeza Financeira",
        "origin": "Suécia",
        "icon": "scissors",
        "tagline": "Auditoria de assinaturas — o Döstädning sueco nas suas finanças",
        "description": "O 'death cleaning' sueco — audite suas assinaturas a cada 90 dias. Detecte gastos esquecidos e cancele o que não usa mais.",
        "benefits": ["Elimina gastos esquecidos", "Economia média de 15%", "Mantém só o essencial"],
        "best_for": "Quem acumulou muitas assinaturas e quer fazer uma faxina nos gastos fixos.",
        "scores": {
            "age": {"under_18": 2, "18_25": 3, "26_35": 4, "36_50": 5, "over_50": 5},
            "monthly_income": {"up_to_1k": 3, "1k_3k": 4, "3k_7k": 4, "7k_15k": 3, "over_15k": 2},
            "income_stability": {"fixed": 4, "variable": 2, "mixed": 3, "uncertain": 2},
            "savings_discipline": {1: 3, 2: 4, 3: 3, 4: 2, 5: 1},
            "spending_personality": {"impulsive": 3, "planned": 3, "balanced": 3, "frugal": 2},
            "financial_literacy": {"beginner": 2, "basic": 4, "intermediate": 4, "advanced": 3},
            "goal_type": {"emergency_fund": 2, "pay_debt": 2, "dream": 2, "invest": 1, "control": 3, "subscriptions": 5},
            "credit_card_use": {"no_card": 2, "full_payment": 3, "partial": 3, "revolving": 4, "multiple": 4},
            "household": {"single": 3, "couple": 4, "family": 5, "roommates": 3},
            "subscription_count": {"none": 0, "1_3": 2, "4_6": 4, "7_plus": 5},
        },
    },
    "envelope_pix": {
        "name": "Envelopes Pix",
        "origin": "Brasil + YNAB",
        "icon": "envelope",
        "tagline": "Zero-sum budgeting com caixinhas digitais",
        "description": "Cada real tem um propósito. Divida sua renda em envelopes por categoria. Se um acaba, realoque de outro. Zero-sum budgeting inspirado no YNAB + Caixinhas Nubank.",
        "benefits": ["Controle total por categoria", "Nunca estoura o orçamento", "Ideal para Pix do dia a dia"],
        "best_for": "Quem quer controle granular sobre cada categoria de gasto e está disposto a gerenciar ativamente.",
        "scores": {
            "age": {"under_18": 2, "18_25": 4, "26_35": 5, "36_50": 4, "over_50": 2},
            "monthly_income": {"up_to_1k": 3, "1k_3k": 4, "3k_7k": 5, "7k_15k": 4, "over_15k": 3},
            "income_stability": {"fixed": 4, "variable": 5, "mixed": 5, "uncertain": 4},
            "savings_discipline": {1: 3, 2: 3, 3: 4, 4: 4, 5: 3},
            "spending_personality": {"impulsive": 3, "planned": 5, "balanced": 3, "frugal": 3},
            "financial_literacy": {"beginner": 2, "basic": 4, "intermediate": 5, "advanced": 3},
            "goal_type": {"emergency_fund": 4, "pay_debt": 4, "dream": 4, "invest": 3, "control": 5, "subscriptions": 3},
            "credit_card_use": {"no_card": 3, "full_payment": 4, "partial": 4, "revolving": 3, "multiple": 4},
            "household": {"single": 4, "couple": 3, "family": 4, "roommates": 4},
            "subscription_count": {"none": 3, "1_3": 4, "4_6": 4, "7_plus": 4},
        },
    },
}

QUESTION_WEIGHTS = {
    "age": 0.8,
    "monthly_income": 1.0,
    "income_stability": 1.5,
    "savings_discipline": 2.0,
    "spending_personality": 1.5,
    "financial_literacy": 1.2,
    "goal_type": 2.0,
    "credit_card_use": 1.0,
    "household": 1.0,
    "subscription_count": 0.8,
}


def calculate_method_scores(answers: dict) -> list[dict]:
    scores = []
    for method_key, profile in METHOD_PROFILES.items():
        total = 0.0
        max_possible = 0.0
        breakdown = []

        for qid, weight in QUESTION_WEIGHTS.items():
            answer = answers.get(qid)
            if answer is None:
                continue
            profile_scores = profile["scores"].get(qid, {})
            if isinstance(answer, int):
                method_score = profile_scores.get(answer, 0)
            else:
                method_score = profile_scores.get(answer, 0)
            weighted = method_score * weight
            total += weighted
            max_possible += 5 * weight
            breakdown.append({
                "question_id": qid,
                "answer": answer,
                "score": method_score,
                "weighted": round(weighted, 1),
            })

        pct = round((total / max_possible) * 100, 1) if max_possible > 0 else 0
        scores.append({
            "key": method_key,
            "name": profile["name"],
            "origin": profile["origin"],
            "icon": profile["icon"],
            "tagline": profile["tagline"],
            "description": profile["description"],
            "benefits": profile["benefits"],
            "best_for": profile["best_for"],
            "score": round(total, 1),
            "max_score": round(max_possible, 1),
            "percentage": pct,
            "breakdown": breakdown,
        })

    scores.sort(key=lambda x: x["percentage"], reverse=True)
    return scores


def get_recommendation(answers: dict) -> dict:
    scored = calculate_method_scores(answers)
    top = scored[0] if scored else None
    alternatives = scored[1:4] if len(scored) > 1 else []

    dream_text = answers.get("savings_goal_dream", "")
    dream_advice = None
    if dream_text and top:
        dream_advice = _generate_dream_advice(dream_text, top)

    return {
        "top_recommendation": top,
        "all_scores": scored,
        "alternatives": alternatives,
        "dream_advice": dream_advice,
    }


def _generate_dream_advice(dream: str, method: dict) -> str:
    return (
        f"Para realizar seu sonho: \"{dream}\", "
        f"recomendamos o método **{method['name']}** ({method['origin']}). "
        f"Ele é ideal porque {method['best_for'].lower()} "
    )
