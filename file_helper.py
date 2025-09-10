from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

def generate_financial_plan_pdf(data: dict, filename="financial_plan.pdf"):
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20
    )
    section_style = styles['Heading2']
    body_style = styles['Normal']

    # Title
    elements.append(Paragraph("Personal Financial Plan", title_style))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph("Summary", section_style))
    elements.append(Paragraph(data['summary'], body_style))
    elements.append(Spacer(1, 12))

    # Helper function for lists
    def add_list_section(title, items):
        elements.append(Paragraph(title, section_style))
        bullet_list = ListFlowable(
            [ListItem(Paragraph(item, body_style)) for item in items],
            bulletType='bullet',
            start='disc'
        )
        elements.append(bullet_list)
        elements.append(Spacer(1, 12))

    # Sections
    add_list_section("Budgeting Recommendations", data['budgeting_recommendations'])
    add_list_section("Savings and Investment", data['savings_and_investment'])
    add_list_section("Debt Management", data['debt_management'])
    add_list_section("Risk and Emergency Planning", data['risk_and_emergency'])
    add_list_section("Next Steps", data['next_steps'])

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF generated: {filename}")



# PDF generation function returning bytes
def generate_pdf_bytes(data: dict):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title_style', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=20)
    section_style = styles['Heading2']
    body_style = styles['Normal']

    elements.append(Paragraph("Personal Financial Plan", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Summary", section_style))
    elements.append(Paragraph(data['summary'], body_style))
    elements.append(Spacer(1, 12))

    def add_list_section(title, items):
        elements.append(Paragraph(title, section_style))
        bullet_list = ListFlowable(
            [ListItem(Paragraph(item, body_style)) for item in items],
            bulletType='bullet',
            start='disc'
        )
        elements.append(bullet_list)
        elements.append(Spacer(1, 12))

    add_list_section("Budgeting Recommendations", data['budgeting_recommendations'])
    add_list_section("Savings and Investment", data['savings_and_investment'])
    add_list_section("Debt Management", data['debt_management'])
    add_list_section("Risk and Emergency Planning", data['risk_and_emergency'])
    add_list_section("Next Steps", data['next_steps'])

    doc.build(elements)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    financial_data = {
        'summary': 'You currently earn a monthly salary of $500, with monthly expenses totaling around $50. At this point, you have no savings. Your financial goal is to purchase a TV costing $400 within 5 months. This means you will need to save an average of $80 per month to reach your target on time, which is about 16% of your salary. Overall, your income and expenses leave some room to save, but careful budgeting will be important to meet your goal within the timeframe.',
        'budgeting_recommendations': [
            'Track all your monthly expenses carefully to identify any unnecessary spending you can reduce or eliminate.',
            'Create a monthly budget that prioritizes essential expenses (like rent, food, utilities) and allocates $80 each month strictly for your TV savings goal.',
            'Limit discretionary spending such as eating out, entertainment, or impulse purchases during these 5 months.',
            'Set up a separate savings jar or account specifically for your TV fund to avoid mixing it with your daily spending money.',
            'Review your budget weekly to stay on track and make adjustments as needed to avoid overspending.'
        ],
        'savings_and_investment': [
            'Focus primarily on saving cash for your TV purchase, since this is a short-term goal with a tight timeline.',
            'Avoid risky investments for this short period; keep your savings in a safe, easily accessible place like a savings account or money envelope.',
            'Once you achieve your immediate goal, consider establishing an emergency fund to cover at least 3 months of expenses, which will provide a financial safety net.',
            'After building your emergency fund, start thinking about longer-term savings goals like retirement and explore low-risk investment options for growing your wealth over time.'
        ],
        'debt_management': [
            'Since no debts are mentioned, ensure you avoid accumulating new debt while saving for your TV.',
            'If you have any unlisted debts, focus on paying them down as soon as possible to free up cash flow for savings.',
            'Avoid using credit cards to finance your TV purchase to prevent paying interest later.'
        ],
        'risk_and_emergency': [
            'Without an emergency fund currently, you are vulnerable to unexpected expenses that could disrupt your savings plan.',
            'Try to set aside at least a small emergency fund gradually after your TV purchase — aiming initially for $150 (about 3 times your monthly expenses) as a starter buffer.',
            'Consider ways to reduce risk, such as having a backup income source or flexible spending options in case your primary income changes.',
            'Make sure to keep your savings accessible in case you need it for urgent expenses.'
        ],
        'next_steps': [
            'Calculate your exact monthly expenses and identify potential areas to reduce spending by as soon as possible.',
            'Open a dedicated savings account or use a physical method (like an envelope) to separate your TV savings from daily money.',
            'Set a fixed amount of $80 to save each month and deposit it immediately when you receive your salary.',
            'Review your progress at the end of each month and adjust your budget if you face difficulty saving enough.',
            'Avoid purchasing the TV until you have saved the full $400 to prevent debt and financial strain.',
            'After buying the TV, begin gradually building an emergency fund to protect your financial stability.',
            'Continue practicing good budgeting habits to support future financial goals beyond this purchase.'
        ]
    }

    generate_financial_plan_pdf(financial_data)
