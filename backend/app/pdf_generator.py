import os
import qrcode

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

from app.config import COMPANY

def generate_qr(receipt_number):

    qr = qrcode.QRCode(
        version=2,
        box_size=5,
        border=2
    )

    qr.add_data(
        f"https://daltonproperty.co.ke/verify/{receipt_number}"
    )

    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    stream = BytesIO()

    img.save(stream)

    stream.seek(0)

    return stream

def generate_receipt(receipt):

    folder = "receipts"

    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/{receipt['receipt_number']}.pdf"

    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        rightMargin=18*mm,
        leftMargin=18*mm,

        topMargin=15*mm,
        bottomMargin=15*mm

    )
    
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0b3d91"),
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=11,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#2e7d32")
    )

    normal = styles["Normal"]

    normal.fontSize = 10

    elements = []
    
        # ===============================
    # COMPANY HEADER
    # ===============================

    logo_path = COMPANY["logo"]

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=45*mm,
            height=45*mm
        )

    else:

        logo = Paragraph(
            "<b>LOGO</b>",
            normal
        )

    company_info = Paragraph(

        f"""
        <font size=18 color="#0b3d91"><b>{COMPANY['name']}</b></font><br/>

        <font size=11 color="#2e7d32">
        {COMPANY['tagline']}
        </font>

        <br/><br/>

        📍 {COMPANY['address']}<br/>

        ☎ {COMPANY['phone']}<br/>

        ✉ {COMPANY['email']}<br/>

        🌐 {COMPANY['website']}
        """,

        normal

    )

    header = Table(

        [

            [
                logo,
                company_info
            ]

        ],

        colWidths=[55*mm,115*mm]

    )

    header.setStyle(

        TableStyle([

            ("VALIGN",(0,0),(-1,-1),"TOP"),

            ("BOTTOMPADDING",(0,0),(-1,-1),10)

        ])

    )

    elements.append(header)

    elements.append(Spacer(1,8))
    
    line = Table(

        [[""]],

        colWidths=[170*mm]

    )

    line.setStyle(

        TableStyle([

            ("LINEBELOW",(0,0),(-1,-1),2,colors.HexColor("#0b3d91"))

        ])

    )

    elements.append(line)

    elements.append(Spacer(1,8))
    
    title = Table(

        [[

            Paragraph(

                "<font color='white'><b>PAYMENT RECEIPT</b></font>",

                title_style

            )

        ]],

        colWidths=[170*mm]

    )

    title.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#0b3d91")),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8)

        ])

    )

    elements.append(title)

    elements.append(Spacer(1,10))
    
        # ==========================================
    # RECEIPT INFORMATION
    # ==========================================

    receipt_table = Table(

        [

            ["Receipt Number", receipt["receipt_number"]],

            ["Payment Date", str(receipt["payment_date"])],

            ["Tenant Name", receipt["tenant_name"]],

            ["Unit Number", receipt["unit_number"]]

        ],

        colWidths=[55*mm,115*mm]

    )

    receipt_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E8F0FE")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#0b3d91")),

            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8),

            ("BACKGROUND",(1,0),(1,-1),colors.white)

        ])

    )

    elements.append(receipt_table)

    elements.append(Spacer(1,12))
    
    elements.append(

        Paragraph(

            "<b>PAYMENT DETAILS</b>",

            heading_style

        )

    )

    elements.append(Spacer(1,5))
    
    payment_table = Table(

        [

            [

                "Description",

                "Value"

            ],

            [

                "Amount Paid",

                f"KES {receipt['amount_paid']:,.2f}"

            ],

            [

                "Remaining Balance",

                f"KES {receipt['remaining_balance']:,.2f}"

            ],

            [

                "Payment Method",

                receipt["payment_method"]

            ],

            [

                "Transaction Ref",

                receipt["transaction_reference"] or "-"

            ]

        ],

        colWidths=[80*mm,90*mm]

    )

    payment_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b3d91")),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8),

            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke)

        ])

    )

    elements.append(payment_table)

    elements.append(Spacer(1,15))
    
        # ==========================================
    # PAID STAMP
    # ==========================================

    paid = Table(

        [[

            Paragraph(

                "<font color='green'><b>✔ PAYMENT RECEIVED</b></font>",

                title_style

            )

        ]],

        colWidths=[170*mm]

    )

    paid.setStyle(

        TableStyle([

            ("BOX",(0,0),(-1,-1),2,colors.green),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("BOTTOMPADDING",(0,0),(-1,-1),10)

        ])

    )

    elements.append(paid)

    elements.append(Spacer(1,15))
    
        # ==========================================
    # QR CODE
    # ==========================================

    qr_stream = generate_qr(receipt["receipt_number"])

    qr = Image(

        qr_stream,

        width=35*mm,

        height=35*mm

    )

    qr_table = Table(

        [

            [

                qr,

                Paragraph(

                    f"""

                    <b>Receipt Verification</b><br/><br/>

                    Receipt Number:<br/>

                    {receipt['receipt_number']}<br/><br/>

                    Scan this QR Code to verify the receipt.

                    """,

                    normal

                )

            ]

        ],

        colWidths=[45*mm,125*mm]

    )

    qr_table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,colors.lightgrey),

            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

            ("BOTTOMPADDING",(0,0),(-1,-1),10),

            ("TOPPADDING",(0,0),(-1,-1),10)

        ])

    )

    elements.append(qr_table)

    elements.append(Spacer(1,20))
    
        # ==========================================
    # SIGNATURE
    # ==========================================

    signature = Table(

        [

            [

                "",

                "____________________________"

            ],

            [

                "",

                "Authorized Signature"

            ]

        ],

        colWidths=[90*mm,80*mm]

    )

    signature.setStyle(

        TableStyle([

            ("ALIGN",(1,0),(1,-1),"CENTER"),

            ("TOPPADDING",(0,0),(-1,-1),8)

        ])

    )

    elements.append(signature)

    elements.append(Spacer(1,20))
    
        # ==========================================
    # FOOTER
    # ==========================================

    footer = Paragraph(

        """

        <font size=9 color='grey'>

        Thank you for choosing Dalton Property Management.<br/>

        This is a computer-generated receipt and does not require a physical signature.<br/><br/>

        support@daltonproperty.co.ke

        </font>

        """,

        ParagraphStyle(

            "Footer",

            alignment=TA_CENTER

        )

    )

    elements.append(footer)
    doc.build(elements)

    return filename