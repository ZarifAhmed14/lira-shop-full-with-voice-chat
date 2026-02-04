import csv
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

class ReportGenerator:
    def __init__(self, logs_file):
        self.logs_file = logs_file
        self.output_pdf = f"voice_report_{int(time.time())}.pdf"

    def generate_charts(self, cost_breakdown):
        # Generate Cost Breakdown Pie Chart
        plt.figure(figsize=(6, 4))
        labels = ['AI (Groq)', 'STT (Whisper)', 'TTS (Edge)']
        sizes = [cost_breakdown['ai'], cost_breakdown['stt'], cost_breakdown['tts']]
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        # Avoid 0 in pie chart
        sizes = [max(s, 0.000001) for s in sizes]
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Voice Bot Cost Breakdown')
        plt.axis('equal')
        plt.savefig('voice_cost_chart.png')
        plt.close()

    def create_pdf(self):
        # Read Data
        total_ai_cost = 0
        total_stt_cost = 0
        total_tts_cost = 0
        total_queries = 0
        voice_queries = 0
        
        if os.path.exists(self.logs_file):
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_queries += 1
                    total_ai_cost += float(row.get('ai_cost', 0))
                    total_stt_cost += float(row.get('stt_cost', 0))
                    total_tts_cost += float(row.get('tts_cost', 0))
                    if row.get('mode') == 'voice':
                        voice_queries += 1
        
        grand_total = total_ai_cost + total_stt_cost + total_tts_cost
        
        # Generate Charts
        self.generate_charts({
            'ai': total_ai_cost,
            'stt': total_stt_cost,
            'tts': total_tts_cost
        })

        doc = SimpleDocTemplate(self.output_pdf, pagesize=letter)
        msgs = []
        styles = getSampleStyleSheet()
        
        # Title
        msgs.append(Paragraph("Lira Cosmetics Voice AI - Final Report", styles['Title']))
        msgs.append(Spacer(1, 24))
        
        # 1. Voice AI Overview
        msgs.append(Paragraph("1. Voice AI Overview", styles['Heading2']))
        intro_text = """
        This project integrates Voice AI capabilities into the Lira Cosmetics Customer Service Chatbot.
        It enables customers to interact naturally via voice commands using Speech-to-Text (STT) 
        and receive spoken responses via Text-to-Speech (TTS).
        """
        msgs.append(Paragraph(intro_text, styles['Normal']))
        msgs.append(Spacer(1, 12))

        # 2. Technology Stack
        msgs.append(Paragraph("2. Voice Technology Stack", styles['Heading2']))
        bullets = [
            "STT: Groq Whisper Large V3 (Fast, High Accuracy)",
            "TTS: Edge TTS (Natural, Free, Zero-Latency)",
            "AI: Groq Llama 3.3 (Inference Engine)"
        ]
        for b in bullets:
            msgs.append(Paragraph(f"• {b}", styles['Normal']))
        msgs.append(Spacer(1, 12))

        # 3. Cost Analysis
        msgs.append(Paragraph("3. Cost Analysis (Simulation Data)", styles['Heading2']))
        
        data = [
            ['Component', 'Total Cost', '% of Total'],
            ['AI Logic', f"${total_ai_cost:.4f}", f"{(total_ai_cost/grand_total)*100:.1f}%"],
            ['STT (Voice Input)', f"${total_stt_cost:.4f}", f"{(total_stt_cost/grand_total)*100:.1f}%"],
            ['TTS (Voice Output)', f"${total_tts_cost:.4f}", f"{(total_tts_cost/grand_total)*100:.1f}%"],
            ['GRAND TOTAL', f"${grand_total:.4f}", "100%"]
        ]
        
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        msgs.append(t)
        msgs.append(Spacer(1, 12))

        # Chart
        if os.path.exists('voice_cost_chart.png'):
            msgs.append(Image('voice_cost_chart.png', width=400, height=300))

        # 4. Recommendation
        msgs.append(Paragraph("4. Recommendation", styles['Heading2']))
        rec_text = """
        The addition of Voice AI increases the cost per interaction significantly due to STT costs, 
        however, using Groq Whisper keeps this manageable compared to other providers. 
        Edge TTS provides a premium experience at zero cost.
        We recommend deploying this feature to enhance accessibility and user engagement.
        """
        msgs.append(Paragraph(rec_text, styles['Normal']))

        doc.build(msgs)
        
        # Cleanup
        if os.path.exists('voice_cost_chart.png'): os.remove('voice_cost_chart.png')

if __name__ == "__main__":
    import glob
    
    # Find latest voice simulation log
    log_files = glob.glob("logs/voice_simulation_*.csv")
    if log_files:
        latest_log = max(log_files, key=os.path.getctime)
        print(f"Generating report for {latest_log}...")
        rg = ReportGenerator(latest_log)
        rg.create_pdf()
        print(f"Report generated: {rg.output_pdf}")
    else:
        print("No voice simulation logs found.")
