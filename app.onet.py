import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time
import itertools

# ==========================================
# ⚙️ ตรวจสอบไลบรารี pdfkit (สำหรับปุ่ม Export PDF)
# ==========================================
try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

# ==========================================
# ตั้งค่าหน้าเพจ Web App & Professional CSS
# ==========================================
st.set_page_config(page_title="Math Competition Pro - Grade 6", page_icon="🏆", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #8e44ad; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(142,68,173,0.3); transition: all 0.3s ease;}
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #732d91; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(142,68,173,0.4); }
    div.stDownloadButton > button { border-radius: 8px; font-weight: bold; border: 1px solid #bdc3c7; }
    div.stDownloadButton > button:hover { border-color: #8e44ad; color: #8e44ad; }
    .main-header { background: linear-gradient(135deg, #2c3e50, #8e44ad); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); transition: background 0.5s ease; }
    .main-header.challenge { background: linear-gradient(135deg, #000000, #c0392b, #8e44ad); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🚀 Math Competition Pro <span style="font-size: 20px; background: #f1c40f; color: #333; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ป.6 Edition</span></h1>
    <p>ระบบสร้างข้อสอบแข่งขันและเตรียมสอบเข้า ม.1 (ป.6) พร้อมเฉลยแบบ Step-by-Step ระบุสมการละเอียดยิบ</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "เจ้านาย", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ญาญ่า", "ปลื้ม", "พายุ", "ไออุ่น", "กะทิ"]
LOCS = ["โรงเรียน", "สวนสัตว์", "สวนสนุก", "ห้างสรรพสินค้า", "ห้องสมุด", "สวนสาธารณะ", "พิพิธภัณฑ์", "ลานกิจกรรม", "ค่ายลูกเสือ"]
ITEMS = ["ลูกแก้ว", "สติกเกอร์", "การ์ดพลัง", "โมเดลรถ", "ตุ๊กตาหมี", "สมุดระบายสี", "ดินสอสี", "ลูกโป่ง"]
SNACKS = ["ช็อกโกแลต", "คุกกี้", "โดนัท", "เยลลี่", "ขนมปัง", "ไอศกรีม", "น้ำผลไม้", "นมเย็น"]
PUBLISHERS = ["สำนักพิมพ์", "โรงพิมพ์", "ฝ่ายวิชาการ", "ร้านถ่ายเอกสาร", "ทีมงานจัดทำเอกสาร", "บริษัทสิ่งพิมพ์"]
WORK_ACTIONS = ["ทาสีบ้าน", "ปลูกต้นไม้", "สร้างกำแพง", "ประกอบหุ่นยนต์", "เก็บขยะ", "จัดหนังสือ"]
ANIMALS = ["แมงมุม", "มดแดง", "กบ", "จิ้งจก", "ตั๊กแตน", "เต่า", "หอยทาก"]

# คลังอิโมจิสำหรับตาชั่ง
ITEM_EMOJI_MAP = {
    "แตงโม": "🍉", "สับปะรด": "🍍", "แอปเปิล": "🍎", "สตรอว์เบอร์รี": "🍓", 
    "ส้ม": "🍊", "มะม่วง": "🥭",
    "หมู": "🐷", "ไก่": "🐔", "กระต่าย": "🐰", "นก": "🐦", 
    "หมี": "🐻", "ลิง": "🐵",
    "รถบรรทุก": "🚛", "รถยนต์": "🚗", "มอเตอร์ไซค์": "🏍️", "จักรยาน": "🚲"
}

box_html = "<span style='display:inline-block; width:24px; height:24px; border:2px solid #c0392b; border-radius:4px; vertical-align:middle; background-color:#fff;'></span>"

def get_vertical_fraction(num, den, color="#333", is_bold=True):
    weight = "bold" if is_bold else "normal"
    return f"""<span style="display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 6px; font-family:'Sarabun', sans-serif; white-space:nowrap;"><span style="border-bottom:2px solid {color}; padding:2px 6px; font-weight:{weight}; color:{color};">{num}</span><span style="padding:2px 6px; font-weight:{weight}; color:{color};">{den}</span></span>"""

def lcm_multiple(*args):
    res = args[0]
    for i in args[1:]: 
        res = abs(res * i) // math.gcd(res, i)
    return res

def draw_rope_cutting_svg(layers, cuts):
    visual_layers = min(layers, 6)
    width = 300
    height = 50 + (visual_layers * 20) + 40
    
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}" style="background-color:#fafbfc; border-radius:8px; border:2px dashed #bdc3c7; padding:10px;">'
    svg += f'<text x="150" y="25" font-family="Sarabun" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">เชือกพับทบ {layers} ชั้น</text>'
    
    start_y = 45
    layer_spacing = 20
    for i in range(visual_layers):
        y = start_y + (i * layer_spacing)
        svg += f'<line x1="30" y1="{y}" x2="270" y2="{y}" stroke="#e67e22" stroke-width="6" stroke-linecap="round"/>'
        if i == visual_layers - 2 and layers > 6:
            mid_y = y + (layer_spacing / 2)
            svg += f'<text x="150" y="{mid_y + 6}" font-family="sans-serif" font-size="20" font-weight="bold" fill="#d35400" text-anchor="middle">. . .</text>'
            
    cut_spacing = 240 / (cuts + 1)
    for i in range(1, cuts + 1):
        cx = 30 + i * cut_spacing
        end_y = start_y + (visual_layers - 1) * layer_spacing + 15
        svg += f'<line x1="{cx}" y1="35" x2="{cx}" y2="{end_y}" stroke="#e74c3c" stroke-width="3" stroke-dasharray="5,5"/>'
        svg += f'<text x="{cx}" y="32" font-family="sans-serif" font-size="16" fill="#e74c3c" text-anchor="middle">✂️</text>'
        
    svg += f'<text x="150" y="{height - 15}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">1 รอยตัด ตัดผ่านเชือก {layers} เส้นพอดี!</text>'
    svg += '</svg></div>'
    return svg

def get_unit(item_name):
    if item_name in ["หมู", "ไก่", "กระต่าย", "นก", "หมี", "ลิง"]: 
        return "ตัว"
    elif item_name in ["รถบรรทุก", "รถยนต์", "มอเตอร์ไซค์", "จักรยาน"]: 
        return "คัน"
    elif item_name in ["แตงโม", "สับปะรด", "แอปเปิล", "สตรอว์เบอร์รี", "ส้ม", "มะม่วง"]: 
        return "ผล"
    return "ชิ้น"

def draw_balance_scale_html(item_L, qty_L, item_R, qty_R):
    emoji_L = ITEM_EMOJI_MAP.get(item_L, "📦")
    emoji_R = ITEM_EMOJI_MAP.get(item_R, "📦")
    unit_L = get_unit(item_L)
    unit_R = get_unit(item_R)
    
    left_emojis = "".join([f"<span style='font-size:35px; margin:0 2px;'>{emoji_L}</span>"] * qty_L)
    right_emojis = "".join([f"<span style='font-size:35px; margin:0 2px;'>{emoji_R}</span>"] * qty_R)
    
    left_label = f"<div style='font-size:16px; font-weight:bold; color:#2c3e50; margin-top:8px; background:#ecf0f1; border:2px solid #bdc3c7; border-radius:10px; display:inline-block; padding:2px 10px;'>{item_L} {qty_L} {unit_L}</div>"
    right_label = f"<div style='font-size:16px; font-weight:bold; color:#2c3e50; margin-top:8px; background:#ecf0f1; border:2px solid #bdc3c7; border-radius:10px; display:inline-block; padding:2px 10px;'>{item_R} {qty_R} {unit_R}</div>"
    
    html = f"""
    <div style="display: flex; align-items: flex-end; justify-content: center; background: #fdfefe; border-radius: 12px; padding: 20px 15px 15px; margin: 15px auto; width: 85%; border: 3px solid #bdc3c7; box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);">
        <div style="flex: 1; text-align: center; line-height: 1.2;">
            <div>{left_emojis}</div>
            {left_label}
        </div>
        <div style="flex: 0 0 60px; text-align: center; padding-bottom: 25px;">
            <div style="width: 100%; height: 6px; background-color: #2c3e50; border-radius: 3px;"></div>
            <div style="width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-bottom: 20px solid #e74c3c; margin: 0 auto;"></div>
        </div>
        <div style="flex: 1; text-align: center; line-height: 1.2;">
            <div>{right_emojis}</div>
            {right_label}
        </div>
    </div>
    """
    return html

# ==========================================
# 2. ฐานข้อมูลหัวข้อข้อสอบสำหรับ ป.6
# ==========================================
p6_topics = [
    "การสร้างจำนวนจากเลขโดด (ทริคสมดุล)", 
    "โจทย์ปัญหาทำผิดเป็นถูก (สมการ)", 
    "อสมการและค่าที่เป็นไปได้",
    "งานและเวลา (Work & Time)",
    "ระฆังและไฟกะพริบ (ค.ร.น.)",
    "แผนภาพความชอบ (เซต)",
    "ผลบวกจำนวนเรียงกัน (Gauss)",
    "ตรรกะการจับมือ (ทักทาย)",
    "การตัดเชือกพับทบ",
    "โปรโมชั่นแลกของ",
    "หยิบของในที่มืด"
]

# ==========================================
# 3. Logic Generator 
# ==========================================
def generate_questions_logic(sub_t, num_q, is_challenge):
    questions = []
    seen = set()

    for _ in range(num_q):
        q = ""
        sol = ""
        attempts = 0
        
        while attempts < 500:
            attempts += 1
            if sub_t == "🌟 สุ่มรวมทุกแนว (ป.6)":
                actual_sub_t = random.choice(p6_topics)
            else:
                actual_sub_t = sub_t
                
            name = random.choice(NAMES)

            # ---------------------------------------------------------
            if actual_sub_t == "การสร้างจำนวนจากเลขโดด (ทริคสมดุล)":
                if is_challenge:
                    digits = random.sample(range(1, 10), 5)
                    max_prod = 0
                    best_pair = ()
                    for p in itertools.permutations(digits):
                        n1 = p[0]*100 + p[1]*10 + p[2]
                        n2 = p[3]*10 + p[4]
                        if n1 * n2 > max_prod: 
                            max_prod = n1 * n2
                            best_pair = (n1, n2)
                            
                    sd = sorted(digits, reverse=True)
                    
                    q = f"<b>{name}</b> ได้รับบัตรตัวเลข 5 ใบ คือ <b>{', '.join(map(str, digits))}</b> นำมาสร้างเป็น <b>จำนวน 3 หลัก</b> และ <b>จำนวน 2 หลัก</b> ที่คูณกันแล้วได้ <b>'ผลคูณที่มีค่ามากที่สุด'</b> ผลคูณนั้นคือเท่าไร?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (หลักการคูณสมดุล):</b><br>
                    การจะทำให้ผลคูณมีค่ามากที่สุด เราต้องวางตัวเลขค่ามากไว้ในตำแหน่งที่จะไปคูณกับเลขตัวอื่นได้เยอะที่สุด (นั่นคือหลักด้านหน้าสุด)<br>
                    <b>ขั้นตอนที่ 1: เรียงตัวเลขจากมากไปน้อย</b><br>
                    👉 จะได้ตัวเลขคือ: <b>{sd[0]} > {sd[1]} > {sd[2]} > {sd[3]} > {sd[4]}</b><br>
                    <b>ขั้นตอนที่ 2: วางตำแหน่งเพื่อการ "คูณไขว้"</b><br>
                    👉 <b>ตำแหน่งที่ 1 (หลักที่ใหญ่ที่สุด):</b> เราต้องให้เลขตัวที่ 1 ({sd[0]}) และตัวที่ 2 ({sd[1]}) อยู่แยกกัน เพื่อให้มันได้คูณกันเอง<br>
                    &nbsp;&nbsp;&nbsp; <i>ให้ {sd[0]} เป็นหลักสิบของตัวคูณ และ {sd[1]} เป็นหลักร้อยของตัวตั้ง</i><br>
                    👉 <b>ตำแหน่งที่ 2 (ตัวถัดมา):</b> นำเลขตัวที่ 3 ({sd[2]}) ไปอยู่ฝั่งที่มีเลขน้อยกว่า (ฝั่ง {sd[1]}) เพื่อให้โดนไขว้คูณกับเลขที่ใหญ่ที่สุด ({sd[0]})<br>
                    👉 <b>ตำแหน่งที่ 3 (หลักหน่วย):</b> นำเลขที่เหลือมาเรียงไขว้สลับกันให้เกิดความสมดุล ({sd[3]} และ {sd[4]})<br>
                    <b>ขั้นตอนที่ 3: สรุปผลการจัดเรียงและหาคำตอบ</b><br>
                    👉 จากการจัดเรียง จะได้ตัวเลข 2 จำนวนคือ: <b>{best_pair[0]}</b> และ <b>{best_pair[1]}</b><br>
                    👉 นำมาคูณกัน: {best_pair[0]} × {best_pair[1]} = <b>{max_prod:,}</b><br>
                    <b>ตอบ: {max_prod:,}</b></span>"""
                else:
                    digits = random.sample(range(1, 10), 4)
                    max_v = int("".join(map(str, sorted(digits, reverse=True))))
                    min_v = int("".join(map(str, sorted(digits))))
                    
                    q = f"มีบัตรตัวเลข <b>{', '.join(map(str, digits))}</b> จงหาผลต่างของจำนวนที่ <b>มากที่สุด</b> และ <b>น้อยที่สุด</b> ที่สามารถสร้างได้?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: สร้างจำนวนที่มากที่สุด</b><br>
                    👉 นำตัวเลขมาเรียงลำดับจากค่ามากไปหาค่าน้อย จะได้จำนวนคือ <b>{max_v}</b><br>
                    <b>ขั้นตอนที่ 2: สร้างจำนวนที่น้อยที่สุด</b><br>
                    👉 นำตัวเลขมาเรียงลำดับจากค่าน้อยไปหาค่ามาก จะได้จำนวนคือ <b>{min_v}</b><br>
                    <b>ขั้นตอนที่ 3: หาผลต่าง (นำมาลบกัน)</b><br>
                    👉 นำจำนวนที่มากที่สุดตั้ง ลบด้วยจำนวนที่น้อยที่สุด: {max_v} - {min_v} = <b>{max_v-min_v}</b><br>
                    <b>ตอบ: {max_v-min_v}</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาทำผิดเป็นถูก (สมการ)":
                A = random.randint(3, 8)
                B = random.randint(5, 20)
                if is_challenge:
                    X = random.randint(5, 12) * A
                    wrong_ans = (X // A) + B
                    correct_ans = (X * A) - B
                    
                    f_q = get_vertical_fraction('จำนวนปริศนา', A)
                    f_s = get_vertical_fraction('🔲', A, is_bold=False)
                    
                    q = f"<b>{name}</b> ตั้งใจจะนำจำนวนปริศนาจำนวนหนึ่งไป <b>คูณด้วย {A}</b> แล้ว <b>ลบออกด้วย {B}</b><br>แต่เขาทำผิดพลาด สลับไปเขียนในรูปเศษส่วนคือ <b>{f_q}</b> แล้วค่อย <b>บวกเพิ่ม {B}</b> ทำให้ได้ผลลัพธ์เป็น <b>{wrong_ans}</b><br>จงหาผลลัพธ์ที่แท้จริงตามความตั้งใจแรก?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ใช้สมการแก้ปัญหา):</b><br>
                    ให้ 🔲 แทน "จำนวนปริศนา"<br>
                    <b>ขั้นตอนที่ 1: ตั้งสมการจากสิ่งที่ทำผิดพลาด</b><br>
                    👉 สิ่งที่เขียนผิดคือ: {f_s} + {B} = {wrong_ans}<br>
                    <b>ขั้นตอนที่ 2: หาค่า 🔲 ด้วยการแก้สมการทีละขั้น</b><br>
                    👉 กำจัด +{B} โดยนำ {B} ไปลบออกทั้งสองข้าง: <br>
                    &nbsp;&nbsp;&nbsp; {f_s} + {B} <b style='color:red;'>- {B}</b> = {wrong_ans} <b style='color:red;'>- {B}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด:</b> {f_s} = {wrong_ans - B}<br>
                    👉 กำจัดตัวส่วน {A} (การหาร) โดยนำ {A} ไปคูณทั้งสองข้าง: <br>
                    &nbsp;&nbsp;&nbsp; ({f_s}) <b style='color:red;'>× {A}</b> = ({wrong_ans - B}) <b style='color:red;'>× {A}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด:</b> 🔲 = {X} (เราได้จำนวนปริศนาแล้ว!)<br>
                    <b>ขั้นตอนที่ 3: คำนวณใหม่ให้ถูกต้องตามความตั้งใจแรก</b><br>
                    👉 โจทย์สั่งให้ "นำจำนวนปริศนาคูณ {A} แล้วลบ {B}"<br>
                    👉 แทนค่าลงไป: ({X} × {A}) - {B} = {X * A} - {B} = <b>{correct_ans:,}</b><br>
                    <b>ตอบ: {correct_ans:,}</b></span>"""
                else:
                    x = random.randint(5, 20)
                    ans_true = random.randint(30, 80)
                    wrong_ans = ans_true - (2 * x)
                    while wrong_ans <= 0: 
                        ans_true += 10
                        wrong_ans = ans_true - (2 * x)
                        
                    q = f"<b>{name}</b> ตั้งใจจะนำจำนวนหนึ่งไป <b>บวก</b> กับ {x} แต่เขาทำผิดโดยนำไป <b>ลบ</b> ด้วย {x} ทำให้ได้ผลลัพธ์เป็น <b>{wrong_ans}</b><br>ผลลัพธ์ที่แท้จริงคือเท่าไร?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    ให้ 🔲 แทน "จำนวนตอนแรกสุด"<br>
                    <b>ขั้นตอนที่ 1: ตั้งสมการจากสิ่งที่ทำผิด</b><br>
                    👉 สมการที่ทำผิดคือ: 🔲 - {x} = {wrong_ans}<br>
                    <b>ขั้นตอนที่ 2: แก้สมการหาค่า 🔲</b><br>
                    👉 กำจัด -{x} โดยนำ {x} ไปบวกเพิ่มทั้งสองข้าง: <br>
                    &nbsp;&nbsp;&nbsp; 🔲 - {x} <b style='color:red;'>+ {x}</b> = {wrong_ans} <b style='color:red;'>+ {x}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด:</b> 🔲 = {wrong_ans+x}<br>
                    <b>ขั้นตอนที่ 3: คำนวณใหม่ให้ถูกต้องตามโจทย์สั่ง</b><br>
                    👉 ความตั้งใจแรกคือต้องเอาไป <b>บวก</b> ด้วย {x}<br>
                    👉 แทนค่า: {wrong_ans+x} + {x} = <b>{ans_true}</b><br>
                    <b>ตอบ: {ans_true}</b></span>"""

            elif actual_sub_t == "อสมการและค่าที่เป็นไปได้":
                C = random.choice([2, 3, 4, 5])
                ans_list = list(range(random.randint(5, 10), random.randint(12, 18)))
                min_v = ans_list[0]
                max_v = ans_list[-1]
                B = random.randint(3, 8)
                
                if is_challenge:
                    A = (min_v * C) - random.randint(1, C-1)
                    D = (max_v * C) + random.randint(1, C-1)
                    ans = sum(ans_list)
                    
                    f_L = get_vertical_fraction(A, B*C)
                    f_M = get_vertical_fraction("🔲", B)
                    f_R = get_vertical_fraction(D, B*C)
                    
                    q = f"จงหา <b>'ผลบวกของจำนวนนับทุกจำนวน'</b> ที่สามารถเติมในช่องว่างแล้วทำให้อสมการเป็นจริง:<br><br><span style='font-size:24px; font-weight:bold;'>{f_L} &nbsp;&lt;&nbsp; {f_M} &nbsp;&lt;&nbsp; {f_R}</span>"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (อสมการเศษส่วน):</b><br>
                    เป้าหมายคือต้องทำให้ "ตัวส่วนด้านล่างเท่ากัน" ทั้งหมด ถึงจะเปรียบเทียบตัวเศษด้านบนได้!<br>
                    <b>ขั้นตอนที่ 1: ปรับตัวส่วนให้เท่ากัน</b><br>
                    👉 สังเกตว่าเศษส่วนตรงกลางมีส่วนเป็น {B} แต่ซ้ายและขวามีส่วนเป็น {B*C}<br>
                    👉 นำเลข {C} มาคูณทั้งเศษและส่วนตรงกลาง: <br>
                    &nbsp;&nbsp;&nbsp; (🔲 <b style='color:red;'>× {C}</b>) / ({B} <b style='color:red;'>× {C}</b>) ➔ จะได้ตัวส่วนเป็น {B*C} เท่ากับคนอื่นแล้ว<br>
                    <b>ขั้นตอนที่ 2: ตัดตัวส่วนทิ้งแล้วเปรียบเทียบแค่ตัวเศษ</b><br>
                    👉 นำ {B*C} มาคูณตลอดทั้งอสมการเพื่อตัดส่วนทิ้ง จะเหลือแค่:<br>
                    &nbsp;&nbsp;&nbsp; <b>👉 อสมการล่าสุด:</b> {A} &lt; 🔲 × {C} &lt; {D}<br>
                    <b>ขั้นตอนที่ 3: หาจำนวนนับ (🔲) ที่เป็นไปได้</b><br>
                    👉 ท่องสูตรคูณแม่ {C} หาว่าเลขอะไรบ้างที่คูณแล้วได้ผลลัพธ์มากกว่า {A} แต่ต้องน้อยกว่า {D}<br>
                    👉 ตัวเลขที่เข้าเงื่อนไขคือ: <b>{', '.join(map(str, ans_list))}</b><br>
                    <b>ขั้นตอนที่ 4: หาผลบวกตามโจทย์สั่ง</b><br>
                    👉 นำจำนวนทั้งหมดมาบวกกัน: {' + '.join(map(str, ans_list))} = <b>{ans}</b><br>
                    <b>ตอบ: {ans}</b></span>"""
                else:
                    a = random.randint(10, 50)
                    limit_val = random.randint(80, 150)
                    max_val = limit_val - a - 1
                    
                    q = f"จงหา <b>จำนวนนับที่มากที่สุด</b> ที่สามารถเติมในช่องว่างได้:<br><br><span style='font-size:24px; font-weight:bold;'>🔲 + {a} &lt; {limit_val}</span>"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: แก้สมการหาจุดตัด (ขอบเขต)</b><br>
                    👉 กำจัด +{a} โดยนำ {a} มาลบออกทั้งสองข้าง: <br>
                    &nbsp;&nbsp;&nbsp; 🔲 + {a} <b style='color:red;'>- {a}</b> &lt; {limit_val} <b style='color:red;'>- {a}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 อสมการล่าสุด:</b> 🔲 &lt; {limit_val-a}<br>
                    <b>ขั้นตอนที่ 2: หาค่าที่มากที่สุดตามเงื่อนไข</b><br>
                    👉 อสมการอ่านว่า "ช่องว่างต้องมีค่าน้อยกว่า {limit_val-a}" <br>
                    👉 การจะเป็นค่าน้อยกว่าที่มากที่สุดได้ ก็คือตัวเลขที่อยู่ก่อนหน้า {limit_val-a} เพียง 1 แต้ม<br>
                    👉 ดังนั้น 🔲 ที่มากที่สุด = {limit_val-a} - 1 = <b>{max_val}</b><br>
                    <b>ตอบ: {max_val}</b></span>"""

            elif actual_sub_t == "งานและเวลา (Work)":
                action = random.choice(WORK_ACTIONS)
                if is_challenge:
                    n1, n2, n3 = random.sample(NAMES, 3)
                    pairs = [(10, 12, 15, 4), (12, 15, 20, 5), (6, 10, 15, 3), (12, 24, 8, 4)]
                    w1, w2, w3, ans = random.choice(pairs)
                    
                    f1_s = get_vertical_fraction(1, w1, is_bold=False)
                    f2_s = get_vertical_fraction(1, w2, is_bold=False)
                    f3_s = get_vertical_fraction(1, w3, is_bold=False)
                    
                    lcm_val = lcm_multiple(w1, w2, w3)
                    sum_num = (lcm_val//w1) + (lcm_val//w2) + (lcm_val//w3)
                    
                    f_total = get_vertical_fraction(sum_num, lcm_val, is_bold=True)
                    f_ans = get_vertical_fraction(1, ans, is_bold=False)
                    
                    q = f"ในการ<b>{action}</b> หากให้ <b>{n1}</b> ทำคนเดียวจะเสร็จใน {w1} วัน, <b>{n2}</b> ทำคนเดียวเสร็จใน {w2} วัน, และ <b>{n3}</b> ทำคนเดียวเสร็จใน {w3} วัน<br>จงหาว่าถ้าทั้งสามคน 'ช่วยกันทำพร้อมกัน' งานนี้จะเสร็จภายในเวลากี่วัน?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (เรื่องอัตราการทำงาน):</b><br>
                    เป้าหมายคือ ต้องเปลี่ยนเวลาทำงานเต็มก้อน ให้กลายเป็น "ปริมาณงานที่ทำได้ใน 1 วัน" ก่อน!<br>
                    <b>ขั้นตอนที่ 1: หาผลงานใน 1 วันของแต่ละคน (แปลงเป็นเศษส่วน)</b><br>
                    👉 {n1} ใช้เวลา {w1} วัน ➔ 1 วันทำได้ {f1_s} ของงาน<br>
                    👉 {n2} ใช้เวลา {w2} วัน ➔ 1 วันทำได้ {f2_s} ของงาน<br>
                    👉 {n3} ใช้เวลา {w3} วัน ➔ 1 วันทำได้ {f3_s} ของงาน<br>
                    <b>ขั้นตอนที่ 2: นำผลงานใน 1 วันมารวมกัน</b><br>
                    👉 ถ้าช่วยกันทำ แปลว่าต้องเอาเศษส่วนมาบวกกัน: {f1_s} + {f2_s} + {f3_s}<br>
                    👉 หา ค.ร.น. ของตัวส่วน ({w1}, {w2}, {w3}) จะได้ <b>{lcm_val}</b><br>
                    👉 ปรับตัวส่วนให้เป็น {lcm_val} และบวกตัวเศษ จะได้ยอดรวมเท่ากับ {f_total}<br>
                    👉 ทำเป็นเศษส่วนอย่างต่ำ จะได้ <b>{f_ans} ของงาน</b> (แปลว่า 3 คนช่วยกัน 1 วัน ทำงานได้ {f_ans} ส่วน)<br>
                    <b>ขั้นตอนที่ 3: พลิกเศษส่วนกลับเพื่อหาจำนวนวันทั้งหมด</b><br>
                    👉 พลิกจาก 1 ส่วน {ans} กลับขึ้นมาด้านบน จะได้คำตอบคือ <b>{ans} วัน</b> งานถึงจะเสร็จสมบูรณ์ 100%<br>
                    <b>ตอบ: {ans} วัน</b></span>"""
                else:
                    pairs = [(3,6,2), (4,12,3), (6,12,4), (10,15,6)]
                    w1, w2, ans = random.choice(pairs)
                    n1, n2 = random.sample(NAMES, 2)
                    
                    q = f"ในการ<b>{action}</b> หากให้ <b>{n1}</b> ทำคนเดียวจะเสร็จใน {w1} วัน แต่ถ้าให้ <b>{n2}</b> ทำคนเดียวจะเสร็จใน {w2} วัน <br>จงหาว่าถ้าช่วยกันทำพร้อมกัน จะเสร็จภายในเวลากี่วัน?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: ใช้สูตรลัดเรื่อง 2 คนช่วยกันทำงาน</b><br>
                    👉 สูตรคือ: <b>(เวลาคนแรก × เวลาคนที่สอง) ÷ (เวลาคนแรก + เวลาคนที่สอง)</b><br>
                    <b>ขั้นตอนที่ 2: แทนค่าตัวเลขลงในสูตร</b><br>
                    👉 หาผลคูณด้านบน: {w1} × {w2} = <b>{w1*w2}</b><br>
                    👉 หาผลบวกด้านล่าง: {w1} + {w2} = <b>{w1+w2}</b><br>
                    <b>ขั้นตอนที่ 3: นำผลลัพธ์มาหารกัน</b><br>
                    👉 นำ {w1*w2} ÷ {w1+w2} = <b>{ans} วัน</b><br>
                    <b>ตอบ: {ans} วัน</b></span>"""

            elif actual_sub_t == "ระฆังและไฟกะพริบ (ค.ร.น.)":
                item_word = random.choice(["สัญญาณไฟ", "นาฬิกาปลุก", "ระฆัง"])
                if is_challenge:
                    l1, l2, l3, l4 = random.sample([10, 15, 20, 30, 45, 60], 4)
                    lcm = lcm_multiple(l1, l2, l3, l4)
                    ans_min = lcm // 60
                    ans_sec = lcm % 60
                    text_ans = f"{ans_min} นาที" if ans_sec == 0 else f"{ans_min} นาที {ans_sec} วินาที"
                    
                    q = f"<b>{item_word} 4 ชิ้น</b> ทำงานด้วยจังหวะที่ต่างกัน ดังนี้:<br>ชิ้นที่ 1 ดังทุกๆ {l1} วินาที, ชิ้นที่ 2 ดังทุกๆ {l2} วินาที, ชิ้นที่ 3 ดังทุกๆ {l3} วินาที, และชิ้นที่ 4 ดังทุกๆ {l4} วินาที <br>ถ้าเพิ่งดังพร้อมกันไป อีกกี่นาทีข้างหน้าจึงจะดังพร้อมกันอีกครั้ง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    โจทย์ที่มีคำว่า "เกิดขึ้นพร้อมกันอีกครั้ง" คือการหา <b>ค.ร.น. (ตัวคูณร่วมน้อย)</b> เสมอ!<br>
                    <b>ขั้นตอนที่ 1: ตั้งหารสั้นเพื่อหา ค.ร.น.</b><br>
                    👉 นำตัวเลขรอบเวลาทั้ง 4 ตัว คือ {l1}, {l2}, {l3}, {l4} มาตั้งหารสั้น<br>
                    👉 เมื่อคูณตัวเลขที่ได้จากการหารสั้นทั้งหมด จะได้ ค.ร.น. = <b>{lcm} วินาที</b> (นี่คือเวลาที่มันจะดังพร้อมกันอีกครั้ง)<br>
                    <b>ขั้นตอนที่ 2: แปลงหน่วยวินาทีเป็นนาทีและวินาที</b><br>
                    👉 เนื่องจาก 1 นาที มี 60 วินาที ให้นำ {lcm} มาตั้งหารด้วย 60<br>
                    👉 {lcm} ÷ 60 จะได้ผลลัพธ์เป็น <b>{text_ans}</b> พอดี<br>
                    <b>ตอบ: {text_ans}</b></span>"""
                else:
                    l1, l2, l3 = random.sample([10, 12, 15, 20, 30], 3)
                    lcm = lcm_multiple(l1, l2, l3)
                    
                    q = f"{item_word} 3 ชิ้น ทำงานด้วยจังหวะต่างกัน ชิ้นแรกดังทุกๆ {l1} วินาที, ชิ้นที่สอง {l2} วินาที และชิ้นที่สาม {l3} วินาที <br>ถ้าเพิ่งดังพร้อมกันไป อีกกี่วินาทีข้างหน้าจึงจะดังพร้อมกันอีกครั้ง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: วิเคราะห์แนวโจทย์</b><br>
                    👉 โจทย์ที่ถามหาเวลาที่สิ่งของจะ 'เกิดขึ้นพร้อมกันอีกครั้ง' เราจะต้องใช้การหา <b>ค.ร.น. (ตัวคูณร่วมน้อย)</b><br>
                    <b>ขั้นตอนที่ 2: ตั้งหารสั้น</b><br>
                    👉 นำรอบเวลาทั้งหมดคือ {l1}, {l2}, และ {l3} มาตั้งหารสั้น<br>
                    👉 เมื่อนำตัวเลขด้านหน้าและด้านล่างมาคูณกัน จะได้ผลลัพธ์ ค.ร.น. เท่ากับ <b>{lcm}</b><br>
                    👉 แสดงว่าอีก {lcm} วินาที วงจรรอบเวลาของทั้ง 3 ชิ้นจะวนมาเจอกันพอดี<br>
                    <b>ตอบ: อีก {lcm} วินาที</b></span>"""

            elif actual_sub_t == "การตัดเชือกพับทบ":
                name = random.choice(NAMES)
                if is_challenge:
                    f = random.randint(3, 5)
                    c = random.randint(3, 6)
                    layers = 2**f
                    ans = layers * c + 1
                    
                    svg_graphic = draw_rope_cutting_svg(layers, c)
                    q = f"<b>{name}</b> นำเชือกมาพับทบครึ่งซ้อนกันไปเรื่อยๆ จำนวน <b>{f} ครั้ง</b> จากนั้นใช้กรรไกรตัดเชือกให้ขาดออก <b>{c} รอยตัด</b> <br>เมื่อคลี่เชือกทั้งหมดออกมา จะได้เศษเชือกชิ้นเล็กชิ้นน้อยรวมทั้งหมดกี่เส้น?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาความหนา (จำนวนชั้น) ของเชือกหลังจากถูกพับ</b><br>
                    👉 การพับครึ่ง 1 ครั้ง ความหนาของเชือกจะถูกคูณ 2 เสมอ<br>
                    👉 ถ้าพับ {f} ครั้ง = 2 ยกกำลัง {f} (2 × 2 ×... ไป {f} ครั้ง) = <b>{layers} ชั้น</b><br>
                    <b>ขั้นตอนที่ 2: เข้าใจหลักการตัดเชือก</b><br>
                    👉 การเอากรรไกรตัดตรงกลางเชือก 1 ครั้ง จะสร้างเชือกเส้นใหม่ได้เท่ากับ "ความหนาของชั้น" พอดี<br>
                    👉 ดังนั้น ถ้าเราตัด {c} รอย จะได้จำนวนเชือกเส้นใหม่เพิ่มขึ้นมา = {layers} ชั้น × {c} รอยตัด = <b>{layers*c} เส้น</b><br>
                    <b>ขั้นตอนที่ 3: สรุปคำตอบ</b><br>
                    👉 นำจำนวนเชือกที่ถูกตัดเพิ่ม มาบวกรวมกับเชือกเส้นยาวตั้งต้นที่มีอยู่แล้ว 1 เส้น<br>
                    👉 จะได้ {layers*c} + 1 = <b>{ans} เส้น</b><br>{svg_graphic}
                    <b>ตอบ: {ans} เส้น</b></span>"""
                else:
                    f = 2
                    c = random.randint(2, 4)
                    layers = 2**f
                    ans = layers * c + 1
                    
                    svg_graphic = draw_rope_cutting_svg(layers, c)
                    q = f"<b>{name}</b>นำเชือกมาพับทบครึ่ง <b>{f}</b> ครั้ง จากนั้นตัดให้ขาด <b>{c}</b> รอยตัด <br>เมื่อคลี่ออกมาจะได้เชือกทั้งหมดกี่เส้น?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาความหนาของชั้นเชือก</b><br>
                    👉 พับ {f} ครั้ง ความหนาคือ 2 ยกกำลัง {f} = <b>{layers} ชั้น</b><br>
                    <b>ขั้นตอนที่ 2: คำนวณเส้นที่ถูกตัดและรวมเส้นตั้งต้น</b><br>
                    👉 ตัด {c} รอย จะได้เส้นเชือกเพิ่มขึ้น = จำนวนชั้น × รอยตัด ➔ {layers} × {c} = <b>{layers*c} เส้น</b><br>
                    👉 นำไปบวกกับเชือกเส้นดั้งเดิมอีก 1 เส้น: {layers*c} + 1 = <b>{ans} เส้น</b><br>{svg_graphic}
                    <b>ตอบ: {ans} เส้น</b></span>"""

            elif actual_sub_t == "โปรโมชั่นแลกของ":
                snack = random.choice(SNACKS)
                if is_challenge:
                    exch = random.choice([3, 4, 5])
                    start_bottles = random.randint(20, 40)
                    
                    total_drank = start_bottles
                    empties = start_bottles
                    while empties >= exch:
                        new_b = empties // exch
                        left_b = empties % exch
                        total_drank += new_b
                        empties = new_b + left_b
                        
                    borrowed = 0
                    if empties == exch - 1:
                        borrowed = 1
                        total_drank += 1
                        
                    q = f"โปรโมชั่น: นำซอง<b>{snack}</b>เปล่า <b>{exch}</b> ซอง แลกใหม่ฟรี 1 ชิ้น <br><b>{name}</b> ซื้อ<b>{snack}</b>มา <b>{start_bottles}</b> ชิ้น และเมื่อแลกจนหมดเขาสามารถ <b>'ยืมซองเปล่าเพื่อนมาแลกก่อน 1 ซอง และคืนให้เพื่อนภายหลังได้'</b><br>เขาจะได้กินรวมทั้งหมดกี่ชิ้น?"
                    
                    if borrowed > 0:
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (รวมทริคการยืม):</b><br>
                        <b>ขั้นตอนที่ 1: นำของเดิมที่มีอยู่ไปแลกเป็นทอดๆ ตามปกติก่อน</b><br>
                        👉 นำซองเปล่าทั้งหมดหารด้วย {exch} เพื่อแลกชิ้นใหม่ กินเสร็จก็เอาซองไปแลกซ้ำๆ <br>
                        👉 เมื่อคำนวณการแลกจนกว่าจะแลกต่อไม่ได้ จะพบว่าเขาได้กินและเหลือเศษซองเปล่าตอนจบ <b>{empties} ซอง</b><br>
                        <b>ขั้นตอนที่ 2: ใช้ทริคการยืมของเพื่อน</b><br>
                        👉 เนื่องจากโปรโมชั่นต้องใช้ {exch} ซอง และตอนนี้เขาขาดอีกแค่ 1 ซองเท่านั้น!<br>
                        👉 เขาจึงขอยืมเพื่อนมา 1 ซอง (เมื่อนำมารวมกับที่มีอยู่ ก็จะกลายเป็น {exch} ซองพอดีเป๊ะ)<br>
                        <b>ขั้นตอนที่ 3: แลกของและคืนของ</b><br>
                        👉 นำ {exch} ซองนี้ไปแลก จะได้กินฟรีอีก 1 ชิ้น! <br>
                        👉 และเมื่อกินเสร็จ จะมีซองเปล่าเหลือจากชิ้นนี้ 1 ซอง จึงนำซองนี้ไป <b>'คืนเพื่อน'</b> ได้พอดีไม่มีหนี้สินติดค้าง!<br>
                        👉 รวมจำนวนชิ้นที่ได้กินทั้งหมดแล้วคือ <b>{total_drank} ชิ้น</b><br>
                        <b>ตอบ: {total_drank} ชิ้น</b></span>"""
                    else:
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: แลกตามปกติ</b><br>
                        👉 นำซองเปล่าทั้งหมดหารด้วย {exch} เพื่อแลกชิ้นใหม่ กินเสร็จก็เอาซองไปแลกซ้ำๆ เป็นทอดๆ<br>
                        👉 เมื่อแลกจนหมดจะเหลือเศษซองเปล่าตอนจบ <b>{empties} ซอง</b><br>
                        <b>ขั้นตอนที่ 2: ตรวจสอบเงื่อนไขการยืม</b><br>
                        👉 เนื่องจากเขาเหลือเศษซองเปล่าไม่ถึงจุดที่ 'ขาดอีกแค่ 1 ซอง' จึงไม่เข้าเงื่อนไขที่จะสามารถยืมเพื่อน 1 ซองเพื่อไปแลกแล้วมีซองคืนให้เพื่อนได้<br>
                        👉 ดังนั้นจึงแลกต่อไม่ได้แล้ว รวมได้กินทั้งหมด <b>{total_drank} ชิ้น</b><br>
                        <b>ตอบ: {total_drank} ชิ้น</b></span>"""
                else:
                    exch = 3 if is_p12 else (random.randint(4, 5) if is_p34 else random.randint(5, 8))
                    start_bottles = random.randint(6, 9) if is_p12 else (random.randint(12, 25) if is_p34 else random.randint(30, 60))
                    
                    total_drank = start_bottles
                    empties = start_bottles
                    while empties >= exch:
                        new_b = empties // exch
                        left_b = empties % exch
                        total_drank += new_b
                        empties = new_b + left_b
                        
                    q = f"โปรโมชั่น: นำซอง<b>{snack}</b>เปล่า <b>{exch}</b> ซอง แลกใหม่ฟรี 1 ชิ้น <br>ถ้าซื้อตอนแรก <b>{start_bottles}</b> ชิ้น จะได้กินรวมทั้งหมดกี่ชิ้น?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1:</b> กินรอบแรก {start_bottles} ชิ้น จะได้ซองเปล่า {start_bottles} ซอง<br>
                    <b>ขั้นตอนที่ 2:</b> นำซองเปล่าไปแลก ➔ นำจำนวนซองตั้ง หารด้วย {exch} ➔ จะได้กินชิ้นใหม่ และเหลือเศษซองเปล่าที่ไม่พอแลก<br>
                    <b>ขั้นตอนที่ 3:</b> เมื่อกินชิ้นใหม่เสร็จ ให้นำซองเปล่าที่ได้ ไปรวมกับเศษซองเปล่าที่เหลือจากรอบก่อนหน้า เพื่อสะสมนำไปแลกเป็นทอดๆ ต่อไปเรื่อยๆ จนกว่าซองจะเหลือน้อยกว่า {exch}<br>
                    <b>ขั้นตอนที่ 4:</b> นำยอดจำนวนชิ้นที่ได้กินในทุกๆ รอบมาบวกเข้าด้วยกัน จะได้ผลรวมทั้งหมด <b>{total_drank} ชิ้น</b><br>
                    <b>ตอบ: {total_drank} ชิ้น</b></span>"""

            elif actual_sub_t == "หยิบของในที่มืด":
                item = random.choice(ITEMS)
                if is_challenge:
                    c1 = random.randint(10, 20)
                    c2 = random.randint(10, 20)
                    c3 = random.randint(10, 20)
                    arr = sorted([c1, c2, c3], reverse=True)
                    ans = arr[0] + arr[1] + 1
                    
                    q = f"ในกล่องทึบมี<b>{item}</b>สีแดง <b>{c1}</b> ชิ้น, สีน้ำเงิน <b>{c2}</b> ชิ้น, และสีเขียว <b>{c3}</b> ชิ้น<br>หากหลับตาหยิบ ต้องหยิบออกมา<b>อย่างน้อยที่สุดกี่ชิ้น</b> จึงจะมั่นใจ 100% ว่าจะได้ <b>'ครบทั้ง 3 สี อย่างน้อยสีละ 1 ชิ้น'</b> แน่นอน?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (หลักการดวงซวยที่สุดขั้นสูง):</b><br>
                    เพื่อให้เรากล้ารับประกัน 100% ว่าจะได้ครบทุกสี เราต้องคิดถึงกรณีที่เรา "โชคร้ายที่สุดในชีวิต" คือหยิบกี่ครั้งก็ได้แต่สีซ้ำๆ กันที่มีจำนวนเยอะๆ จนมันหมดกล่องก่อน!<br>
                    <b>ขั้นตอนที่ 1: หาสีที่มีจำนวนเยอะที่สุด 2 อันดับแรก</b><br>
                    👉 สีที่มีจำนวนเยอะที่สุด 2 ลำดับแรกคือสีที่มี <b>{arr[0]} ชิ้น</b> และ <b>{arr[1]} ชิ้น</b><br>
                    <b>ขั้นตอนที่ 2: จำลองความโชคร้าย</b><br>
                    👉 โชคร้ายสุดๆ คือหยิบได้แค่ 2 สีนี้ออกมาหมดเกลี้ยงกล่องเลย: {arr[0]} + {arr[1]} = <b>{arr[0]+arr[1]} ชิ้น</b><br>
                    👉 (ตอนนี้มีของเต็มมือตั้ง {arr[0]+arr[1]} ชิ้น แต่มันมีแค่ 2 สีเท่านั้นนะ!)<br>
                    <b>ขั้นตอนที่ 3: หยิบเพื่อปิดจ๊อบ</b><br>
                    👉 ในกล่องตอนนี้จะเหลือแต่ 'สีที่ 3' ล้วนๆ แล้ว! ดังนั้นการหลับตาหยิบชิ้นต่อไป (หยิบเพิ่ม 1 ชิ้น) จะการันตีร้อยเปอร์เซ็นต์ว่าเราได้สีที่ 3 แน่นอน<br>
                    👉 คำนวณ: {arr[0]+arr[1]} + 1 = <b>{ans} ชิ้น</b><br>
                    <b>ตอบ: {ans} ชิ้น</b></span>"""
                else:
                    c1 = random.randint(15, 30)
                    c2 = random.randint(15, 30)
                    c3 = random.randint(15, 30)
                    c4 = random.randint(5, 15)
                    c_total = c1 + c2 + c3
                    target_color = "สีเหลือง"
                        
                    q = f"ในกล่องทึบมี<b>{item}</b>สีแดง <b>{c1}</b> ชิ้น, สีน้ำเงิน <b>{c2}</b> ชิ้น, สีเขียว <b>{c3}</b> ชิ้น, สีเหลือง <b>{c4}</b> ชิ้น<br>ต้องหลับตาหยิบ<b>อย่างน้อยกี่ชิ้น</b> จึงจะมั่นใจ 100% ว่าจะได้<b>{target_color}</b>อย่างน้อย 1 ชิ้น?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (หลักการดวงซวยที่สุด):</b><br>
                    <b>ขั้นตอนที่ 1: จำลองความโชคร้ายที่สุด</b><br>
                    👉 กรณีที่เราโชคร้ายสุดๆ คือเราอยากได้{target_color} แต่มือเจ้ากรรมดันหยิบได้ "สีอื่นๆ" ออกมาจนหมดเกลี้ยงกล่องก่อนเลย<br>
                    👉 นำจำนวนชิ้นของสีอื่นๆ มารวมกัน: {c1} + {c2} + {c3} = <b>{c_total} ชิ้น</b><br>
                    <b>ขั้นตอนที่ 2: หยิบเพื่อปิดจ๊อบ</b><br>
                    👉 เมื่อเราหยิบสีอื่นจนหมดกล่องแล้ว ของที่เหลือในกล่องตอนนี้จะมีแค่{target_color}เท่านั้น<br>
                    👉 ดังนั้นการหยิบชิ้นต่อไป (หยิบเพิ่ม 1 ชิ้น) จะการันตีร้อยเปอร์เซ็นต์ว่าเป็น{target_color}แน่นอน!<br>
                    👉 คำนวณ: {c_total} + 1 = <b>{c_total+1} ชิ้น</b><br>
                    <b>ตอบ: {c_total+1} ชิ้น</b></span>"""

            elif actual_sub_t == "แผนภาพความชอบ (เซต)":
                n1, n2, n3 = random.sample(SNACKS, 3)
                if is_challenge:
                    tot = random.randint(150, 200)
                    only_A = random.randint(10, 20)
                    only_B = random.randint(10, 20)
                    only_C = random.randint(10, 20)
                    
                    A_B = random.randint(5, 10)
                    B_C = random.randint(5, 10)
                    A_C = random.randint(5, 10)
                    all_3 = random.randint(3, 8)
                    neither = random.randint(5, 15)
                    
                    like_A = only_A + A_B + A_C + all_3
                    like_B = only_B + A_B + B_C + all_3
                    like_C = only_C + A_C + B_C + all_3
                    
                    real_tot = only_A + only_B + only_C + A_B + B_C + A_C + all_3 + neither
                    
                    q = f"สำรวจนักเรียน <b>{real_tot}</b> คน พบว่ามีคนชอบ <b>{n1} {like_A} คน</b>, ชอบ <b>{n2} {like_B} คน</b>, และชอบ <b>{n3} {like_C} คน</b><br>โดยมีคนที่ชอบ {n1}และ{n2} (แต่ไม่ชอบ{n3}) <b>{A_B} คน</b>, ชอบ {n2}และ{n3} (แต่ไม่ชอบ{n1}) <b>{B_C} คน</b>, ชอบ {n1}และ{n3} (แต่ไม่ชอบ{n2}) <b>{A_C} คน</b><br>และคนที่ชอบทั้ง 3 อย่างมี <b>{all_3} คน</b> จงหาว่ามีนักเรียนกี่คนที่ <b>'ไม่ชอบ'</b> ขนมทั้ง 3 ชนิดนี้เลย?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แผนภาพเวนน์ 3 วง):</b><br>
                    เทคนิคคือ ต้องหาคนชอบชนิดเดียวเพียวๆ ให้ได้ก่อน เพื่อป้องกันการนับซ้ำ<br>
                    <b>ขั้นตอนที่ 1: หาคนที่ชอบอย่างใดอย่างหนึ่งล้วนๆ แบบเพียวๆ</b><br>
                    👉 ชอบ {n1} ล้วนๆ = ยอดคนชอบ {n1} - (ยอดที่ซ้อนทับกับวงอื่น) ➔ {like_A} - ({A_B} + {A_C} + {all_3}) = <b>{only_A} คน</b><br>
                    👉 ชอบ {n2} ล้วนๆ = ยอดคนชอบ {n2} - (ยอดที่ซ้อนทับกับวงอื่น) ➔ {like_B} - ({A_B} + {B_C} + {all_3}) = <b>{only_B} คน</b><br>
                    👉 ชอบ {n3} ล้วนๆ = ยอดคนชอบ {n3} - (ยอดที่ซ้อนทับกับวงอื่น) ➔ {like_C} - ({A_C} + {B_C} + {all_3}) = <b>{only_C} คน</b><br>
                    <b>ขั้นตอนที่ 2: รวมคนที่ชอบขนมทั้งหมด (จับทุกชิ้นส่วนในวงกลมมาบวกกัน)</b><br>
                    👉 {only_A} + {only_B} + {only_C} + {A_B} + {B_C} + {A_C} + {all_3} = <b>{real_tot - neither} คน</b> (นี่คือคนที่ชอบอย่างน้อย 1 ชนิด)<br>
                    <b>ขั้นตอนที่ 3: หาคนที่ไม่ชอบเลย (คนที่อยู่นอกวงกลม)</b><br>
                    👉 นำยอดคนทั้งหมดในงาน ลบยอดรวมคนที่ชอบขนม ➔ {real_tot} - {real_tot - neither} = <b>{neither} คน</b><br>
                    <b>ตอบ: {neither} คน</b></span>"""
                else:
                    tot = random.randint(100, 200)
                    both = random.randint(20, 50)
                        
                    only_a = random.randint(10, 20)
                    only_b = random.randint(10, 20)
                    l_a = only_a + both
                    l_b = only_b + both
                    neither = tot - (only_a + only_b + both)
                    
                    q = f"สำรวจนักเรียน <b>{tot}</b> คน พบว่าชอบ<b>{n1}</b> <b>{l_a}</b> คน, ชอบ<b>{n2}</b> <b>{l_b}</b> คน, และชอบทั้งสองอย่าง <b>{both}</b> คน <br>มีกี่คนที่ไม่ชอบกินขนมทั้งสองชนิดนี้เลย?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (เรื่องเซต 2 วง):</b><br>
                    ระวัง! ยอดคนที่ชอบ {n1} และ {n2} นั้น ได้รวมคนที่ชอบทั้ง 2 อย่าง (ส่วนที่ซ้อนทับกัน) เข้าไปแล้ว เราต้องหักออกเพื่อไม่ให้นับเบิ้ล<br>
                    <b>ขั้นตอนที่ 1: หาคนที่ชอบชนิดเดียวล้วนๆ (เพียวๆ)</b><br>
                    👉 ชอบ {n1} อย่างเดียว: นำคนชอบ {n1} ลบยอดตรงกลาง ➔ {l_a} - {both} = <b>{only_a} คน</b><br>
                    👉 ชอบ {n2} อย่างเดียว: นำคนชอบ {n2} ลบยอดตรงกลาง ➔ {l_b} - {both} = <b>{only_b} คน</b><br>
                    <b>ขั้นตอนที่ 2: หาคนที่ชอบขนมทั้งหมด</b><br>
                    👉 นำยอดทั้ง 3 ส่วนมาบวกกัน (ซ้ายเพียว + ขวาเพียว + ตรงกลาง) ➔ {only_a} + {only_b} + {both} = <b>{only_a + only_b + both} คน</b><br>
                    <b>ขั้นตอนที่ 3: หาคนที่ไม่ชอบเลย</b><br>
                    👉 นำคนทั้งหมดลบคนที่ชอบขนม: {tot} - {only_a + only_b + both} = <b>{neither} คน</b><br>
                    <b>ตอบ: {neither} คน</b></span>"""

            elif actual_sub_t == "ตรรกะการจับมือ (ทักทาย)":
                loc = random.choice(LOCS)
                if is_challenge:
                    n_a = random.randint(10, 15)
                    n_b = random.randint(10, 15)
                    ans = n_a * n_b
                    
                    q = f"ในงานกิจกรรมที่<b>{loc}</b> มีเด็กชาย <b>{n_a}</b> คน และเด็กหญิง <b>{n_b}</b> คน<br>ถ้า <b>'เด็กชายทุกคนต้องจับมือทำความรู้จักกับเด็กหญิงทุกคน'</b> (ไม่จับมือกับเพศเดียวกัน) จะมีการจับมือเกิดขึ้นทั้งหมดกี่ครั้ง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (การจับคู่ข้ามกลุ่ม):</b><br>
                    ข้อนี้เราไม่ได้จับมือรวมกันมั่วๆ ทั้งหมด แต่เป็นการจับคู่ข้ามระหว่าง 2 กลุ่มที่แยกกันอย่างชัดเจน!<br>
                    <b>ขั้นตอนที่ 1: มองมุมมองจากเด็กชาย 1 คนก่อน</b><br>
                    👉 เด็กชาย 1 คน จะต้องเดินไปจับมือทำความรู้จักเด็กหญิงให้ครบทั้ง {n_b} คน (นั่นคือเด็กชาย 1 คน สร้างการจับมือได้ {n_b} ครั้ง)<br>
                    <b>ขั้นตอนที่ 2: ขยายผลในภาพรวม</b><br>
                    👉 เนื่องจากในงานนี้มีเด็กชายทั้งหมดตั้ง {n_a} คน ดังนั้นเหตุการณ์การเดินไปจับมือแบบในขั้นตอนที่ 1 จะเกิดขึ้นซ้ำๆ กันถึง {n_a} รอบ<br>
                    <b>ขั้นตอนที่ 3: ใช้สมการการคูณ</b><br>
                    👉 นำจำนวนคนทั้งสองกลุ่มมาคูณกันได้เลย: {n_a} คน × {n_b} คน = <b>{ans:,} ครั้ง</b><br>
                    <b>ตอบ: {ans:,} ครั้ง</b></span>"""
                else:
                    n = random.randint(10, 20)
                    ans = sum(range(1, n))
                    q = f"ในการจัดกิจกรรม มีเด็กมาร่วมงาน <b>{n}</b> คน หากเด็กทุกคนจับมือทำความรู้จักกันให้ครบทุกคน (จับมือกันเองภายในกลุ่ม) จะมีการจับมือเกิดขึ้นทั้งหมดกี่ครั้ง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: คิดภาพการเดินจับมือทีละคน</b><br>
                    👉 <b>คนที่ 1:</b> เดินไปจับมือกับคนอื่นที่เหลือทุกคน จะเกิดการจับ <b>{n-1} ครั้ง</b><br>
                    👉 <b>คนที่ 2:</b> เดินไปจับมือคนอื่น (แต่ไม่ต้องจับคนที่ 1 แล้วเพราะเขาจับมาแล้ว) จะเกิดการจับ <b>{n-2} ครั้ง</b><br>
                    <b>ขั้นตอนที่ 2: สังเกตแพทเทิร์น</b><br>
                    👉 จำนวนครั้งของการจับมือจะลดหลั่นลงไปเรื่อยๆ ทีละ 1 แบบนี้ ➔ {n-1}, {n-2}, {n-3}... ไปจนถึง 1<br>
                    <b>ขั้นตอนที่ 3: คำนวณผลรวม</b><br>
                    👉 นำตัวเลขทั้งหมดมาบวกกัน: {' + '.join(str(x) for x in range(n-1, 0, -1))} = <b>{ans} ครั้ง</b><br>
                    <b>ตอบ: {ans} ครั้ง</b></span>"""

            else:
                q = f"⚠️ [ระบบผิดพลาด] ไม่พบเงื่อนไขสำหรับหัวข้อ: <b>{actual_sub_t}</b>"
                sol = "Error"

            if q not in seen:
                seen.add(q)
                questions.append({"question": q, "solution": sol})
                break
                
    return questions

# ==========================================
# UI Rendering
# ==========================================
def extract_body(html_str):
    try: return html_str.split('<body>')[1].split('</body>')[0]
    except IndexError: return html_str

def create_page(level, sub_t, questions, is_key=False, q_margin="20px", ws_height="180px", brand_name="", is_challenge=False):
    title_suffix = " 🔥 [ULTIMATE CHALLENGE]" if is_challenge else ""
    title = f"เฉลย (Answer Key){title_suffix}" if is_key else f"ข้อสอบ (TMC Edition){title_suffix}"
    
    student_info = """
        <table style="width: 100%; margin-bottom: 10px; font-size: 18px; border-collapse: collapse;">
            <tr>
                <td style="width: 1%; white-space: nowrap; padding-right: 5px;"><b>ชื่อ-สกุล</b></td>
                <td style="border-bottom: 2px dotted #999; width: 60%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>ระดับชั้น</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>เลขที่</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
            </tr>
        </table>
        """ if not is_key else ""
        
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Sarabun', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }}
        .header h2 {{ color: {'#c0392b' if is_challenge else '#8e44ad'}; }}
        .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.8; }}
        .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }}
        .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }}
        .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f5eef8; border-left: 4px solid {'#c0392b' if is_challenge else '#8e44ad'}; border-radius: 4px; line-height: 1.8; }}
        .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
    </style></head><body>
    <div class="header"><h2>{title}</h2><p><b>หมวดหมู่:</b> {sub_t} ({level})</p></div>
    {student_info}"""
    
    for i, item in enumerate(questions, 1):
        html += f'<div class="q-box"><b>ข้อที่ {i}.</b> '
        if is_key:
            html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
        else:
            html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับแสดงวิธีคิดวิเคราะห์...</div><div class="ans-line">ตอบ: </div>'
        html += '</div>'
        
    if brand_name: 
        html += f'<div class="page-footer">&copy; 2026 {brand_name} | สงวนลิขสิทธิ์</div>'
        
    return html + "</body></html>"

# ==========================================
# 4. Streamlit UI (Sidebar & Result Grouping)
# ==========================================
st.sidebar.markdown("## ⚙️ พารามิเตอร์การสร้างข้อสอบ")

# ปรับระดับชั้นให้เน้น ป.6 ตามที่ผู้ใช้ต้องการ
selected_level = st.sidebar.selectbox("🏆 เลือกระดับชั้น:", ["ประถมศึกษาปีที่ 6 (ป.6) - O-NET / สอบเข้า ม.1"])
sub_options = p6_topics
selected_sub = st.sidebar.selectbox("📝 เลือกแนวข้อสอบ (พร้อมเฉลยละเอียด):", sub_options + ["🌟 สุ่มรวมทุกแนว (ป.6)"])

num_input = st.sidebar.number_input("🔢 จำนวนข้อ:", min_value=1, max_value=100, value=10)

st.sidebar.markdown("---")
is_challenge = st.sidebar.toggle("🔥 โหมด Challenge (ระดับยากพิเศษสำหรับเด็กเก่ง)", value=False)

if is_challenge:
    st.markdown("""
    <script>
        const header = window.parent.document.querySelector('.main-header');
        if(header) { header.classList.add('challenge'); header.querySelector('span').innerText = '🔥 Ultimate Challenge Mode'; header.querySelector('span').style.background = '#e74c3c'; header.querySelector('span').style.color = '#fff'; }
    </script>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <script>
        const header = window.parent.document.querySelector('.main-header');
        if(header) { header.classList.remove('challenge'); header.querySelector('span').innerText = 'ป.6 Edition'; header.querySelector('span').style.background = '#f1c40f'; header.querySelector('span').style.color = '#333'; }
    </script>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📏 ตั้งค่าหน้ากระดาษ")
spacing_level = st.sidebar.select_slider(
    "↕️ ความสูงของพื้นที่ทดเลข:", 
    options=["แคบ", "ปานกลาง", "กว้าง", "กว้างพิเศษ"], 
    value="กว้าง"
)

if spacing_level == "แคบ": q_margin, ws_height = "15px", "100px"
elif spacing_level == "ปานกลาง": q_margin, ws_height = "20px", "180px"
elif spacing_level == "กว้าง": q_margin, ws_height = "30px", "280px"
else: q_margin, ws_height = "40px", "400px"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 ตั้งค่าแบรนด์")
brand_name = st.sidebar.text_input("🏷️ ชื่อแบรนด์ / ผู้สอน:", value="บ้านทีเด็ด")

if st.sidebar.button(f"{'🚀 สั่งสร้างข้อสอบระดับ Ultimate Challenge!' if is_challenge else '🚀 สั่งสร้างข้อสอบแข่งขันเดี๋ยวนี้'}", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบข้อสอบ วาดภาพกราฟิกประกอบ และจัดทำเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic(selected_level, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_level, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name, is_challenge=is_challenge)
        html_k = create_page(selected_level, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name, is_challenge=is_challenge)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        bg_color = "#2c3e50" if is_challenge else "#525659"
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: {bg_color}; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .header h2 {{ color: {'#c0392b' if is_challenge else '#8e44ad'}; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.8; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f5eef8; border-left: 4px solid {'#c0392b' if is_challenge else '#8e44ad'}; border-radius: 4px; line-height: 1.8; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}</style></head><body>{ebook_body}</body></html>"""

        mode_name = "Challenge" if is_challenge else "Normal"
        safe_sub = selected_sub.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename_base = f"P6_Pro_{mode_name}_{safe_sub}_{int(time.time())}"
        
        st.session_state['ebook_html'] = full_ebook_html
        st.session_state['filename_base'] = filename_base
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}_Full_EBook.html", full_ebook_html.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_Worksheet.html", html_w.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_AnswerKey.html", html_k.encode('utf-8'))
        st.session_state['zip_data'] = zip_buffer.getvalue()

if 'ebook_html' in st.session_state:
    st.success(f"✅ ลิขสิทธิ์นี้เป็นของ บ้านทีเด็ด เท่านั้น ห้ามนำไปขาย หรือแจกจ่าย ก่อนได้รับอนุญาต จาก บ้านทีเด็ด")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
