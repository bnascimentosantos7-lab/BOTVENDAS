import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# TOKEN do seu bot (substitua pelo token real do @BotFather)
TOKEN = "SEU_TOKEN_AQUI"

# Configurar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Banco de dados de produtos
PRODUTOS = [
    {"id": 1, "nome": "Camiseta Personalizada", "preco": 49.99, "descricao": "Camiseta 100% algodão"},
    {"id": 2, "nome": "Caneca de Cerâmica", "preco": 29.50, "descricao": "Caneca 300ml com impressão"},
    {"id": 3, "nome": "Adesivos (pack 10)", "preco": 15.00, "descricao": "10 adesivos variados"},
    {"id": 4, "nome": "Mouse Pad", "preco": 39.90, "descricao": "Mouse pad antiderrapante"},
    {"id": 5, "nome": "Livro Digital", "preco": 24.99, "descricao": "E-book em PDF"}
]

# Carrinho de compras (armazenamento temporário)
carrinhos = {}

async def start(update: Update, context: CallbackContext):
    """Comando /start - Mensagem inicial com menu"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data='ver_produtos')],
        [InlineKeyboardButton("🛒 Meu Carrinho", callback_data='ver_carrinho')],
        [InlineKeyboardButton("📞 Suporte", callback_data='suporte')],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data='ajuda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Olá *{update.effective_user.first_name}*!\n\n"
        "🛒 *Bem-vindo ao Bot de Vendas!*\n\n"
        "Aqui você pode comprar produtos diretamente pelo Telegram.\n"
        "Use os botões abaixo para navegar:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def ver_produtos(update: Update, context: CallbackContext):
    """Mostra lista de produtos"""
    query = update.callback_query
    await query.answer()
    
    texto = "📦 *NOSSOS PRODUTOS:*\n\n"
    for produto in PRODUTOS:
        texto += f"*{produto['id']}. {produto['nome']}*\n"
        texto += f"   📝 {produto['descricao']}\n"
        texto += f"   💵 R$ {produto['preco']:.2f}\n\n"
    
    # Criar botões para cada produto
    keyboard = []
    for produto in PRODUTOS:
        keyboard.append([InlineKeyboardButton(
            f"🛒 Comprar {produto['nome']} - R${produto['preco']:.2f}",
            callback_data=f'comprar_{produto["id"]}'
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='voltar_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=texto,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def comprar_produto(update: Update, context: CallbackContext):
    """Adiciona produto ao carrinho"""
    query = update.callback_query
    await query.answer()
    
    produto_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    # Encontrar produto
    produto = next((p for p in PRODUTOS if p['id'] == produto_id), None)
    
    if not produto:
        await query.edit_message_text(text="❌ Produto não encontrado.")
        return
    
    # Inicializar carrinho se não existir
    if user_id not in carrinhos:
        carrinhos[user_id] = []
    
    # Adicionar ao carrinho
    carrinhos[user_id].append(produto)
    
    # Botões de ação
    keyboard = [
        [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data='ver_produtos')],
        [InlineKeyboardButton("🛒 Ver Carrinho", callback_data='ver_carrinho')],
        [InlineKeyboardButton("💳 Finalizar Compra", callback_data='finalizar_compra')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"✅ *{produto['nome']}* adicionado ao carrinho!\n\n"
             f"📝 {produto['descricao']}\n"
             f"💰 Preço: R$ {produto['preco']:.2f}\n\n"
             f"📦 Itens no carrinho: {len(carrinhos[user_id])}\n"
             f"💵 Total: R$ {sum(p['preco'] for p in carrinhos[user_id]):.2f}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def ver_carrinho(update: Update, context: CallbackContext):
    """Mostra itens no carrinho"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in carrinhos or not carrinhos[user_id]:
        texto = "🛒 *Seu carrinho está vazio!*\n\nAdicione produtos para continuar."
    else:
        texto = "🛒 *SEU CARRINHO:*\n\n"
        total = 0
        
        for i, produto in enumerate(carrinhos[user_id], 1):
            texto += f"*{i}. {produto['nome']}*\n"
            texto += f"   R$ {produto['preco']:.2f}\n"
            total += produto['preco']
        
        texto += f"\n📦 *Total de itens:* {len(carrinhos[user_id])}\n"
        texto += f"💰 *Valor total:* R$ {total:.2f}"
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data='ver_produtos')],
        [InlineKeyboardButton("🗑️ Esvaziar Carrinho", callback_data='esvaziar_carrinho')],
        [InlineKeyboardButton("💳 Finalizar Compra", callback_data='finalizar_compra')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='voltar_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=texto,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def esvaziar_carrinho(update: Update, context: CallbackContext):
    """Esvazia o carrinho"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id in carrinhos:
        carrinhos[user_id] = []
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data='ver_produtos')],
        [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='voltar_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🗑️ *Carrinho esvaziado com sucesso!*\n\nSeu carrinho agora está vazio.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def finalizar_compra(update: Update, context: CallbackContext):
    """Finaliza a compra"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in carrinhos or not carrinhos[user_id]:
        texto = "🛒 *Seu carrinho está vazio!*\n\nAdicione produtos antes de finalizar."
    else:
        total = sum(p['preco'] for p in carrinhos[user_id])
        
        # Formatar resumo da compra
        resumo = "📋 *RESUMO DA COMPRA:*\n\n"
        for produto in carrinhos[user_id]:
            resumo += f"• {produto['nome']} - R$ {produto['preco']:.2f}\n"
        
        resumo += f"\n💰 *Total: R$ {total:.2f}*\n"
        resumo += f"📦 *Quantidade de itens: {len(carrinhos[user_id])}*\n\n"
        resumo += "✅ *Compra finalizada com sucesso!*\n\n"
        resumo += "📞 Em breve nosso suporte entrará em contato para finalizar o pagamento e envio.\n"
        resumo += "Obrigado pela preferência! 🛍️"
        
        # Limpar carrinho após compra
        carrinhos[user_id] = []
        
        texto = resumo
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Continuar Comprando", callback_data='ver_produtos')],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data='voltar_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=texto,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def suporte(update: Update, context: CallbackContext):
    """Informações de suporte"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data='ver_produtos')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='voltar_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="📞 *SUPORTE AO CLIENTE*\n\n"
             "Para dúvidas, problemas ou informações:\n\n"
             "📧 Email: suporte@botvendas.com\n"
             "🕒 Horário: Seg-Sex, 9h-18h\n"
             "⚡ Resposta em até 24h\n\n"
             "Estamos aqui para ajudar!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def ajuda(update: Update, context: CallbackContext):
    """Menu de ajuda"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data='ver_produtos')],
        [InlineKeyboardButton("📞 Suporte", callback_data='suporte')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='voltar_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="ℹ️ *AJUDA E INFORMAÇÕES*\n\n"
             "📖 *Como usar o bot:*\n"
             "1. Use /start para iniciar\n"
             "2. Navegue pelos produtos\n"
             "3. Adicione itens ao carrinho\n"
             "4. Finalize a compra\n\n"
             "🛒 *Comandos disponíveis:*\n"
             "/start - Inicia o bot\n"
             "/ajuda - Mostra esta mensagem\n\n"
             "⚠️ *Problemas comuns:*\n"
             "• Bot não responde: Tente /start novamente\n"
             "• Carrinho vazio: Adicione produtos primeiro",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def voltar_menu(update: Update, context: CallbackContext):
    """Volta ao menu principal"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data='ver_produtos')],
        [InlineKeyboardButton("🛒 Meu Carrinho", callback_data='ver_carrinho')],
        [InlineKeyboardButton("📞 Suporte", callback_data='suporte')],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data='ajuda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🏠 *MENU PRINCIPAL*\n\n"
             "Escolha uma opção abaixo:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext):
    """Lida com mensagens de texto"""
    if update.message:
        await update.message.reply_text(
            "🤖 Use os botões do menu ou comandos como /start para navegar!"
        )

def main():
    """Função principal para iniciar o bot"""
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    
    # Handlers para callbacks (botões)
    app.add_handler(CallbackQueryHandler(ver_produtos, pattern='^ver_produtos$'))
    app.add_handler(CallbackQueryHandler(ver_carrinho, pattern='^ver_carrinho$'))
    app.add_handler(CallbackQueryHandler(comprar_produto, pattern='^comprar_'))
    app.add_handler(CallbackQueryHandler(esvaziar_carrinho, pattern='^esvaziar_carrinho$'))
    app.add_handler(CallbackQueryHandler(finalizar_compra, pattern='^finalizar_compra$'))
    app.add_handler(CallbackQueryHandler(suporte, pattern='^suporte$'))
    app.add_handler(CallbackQueryHandler(ajuda, pattern='^ajuda$'))
    app.add_handler(CallbackQueryHandler(voltar_menu, pattern='^voltar_menu$'))
    
    # Handler para mensagens de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar o bot
    print("🤖 Bot de Vendas iniciado!")
    print("📡 Aguardando mensagens...")
    app.run_polling()

if __name__ == '__main__':
    main()
