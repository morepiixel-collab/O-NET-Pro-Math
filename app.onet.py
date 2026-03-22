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
st.set_page_config(page_title="O-NET Math Pro - Grade 6", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #e67e22; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(230,126,34,0.3); transition: all 0.3s ease;}
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #d35400; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(230,126,34,0.4); }
    div.stDownloadButton > button { border-radius: 8px; font-weight: bold; border: 1px solid #bdc3c7; }
    div.stDownloadButton > button:hover { border-color: #e67e22; color: #e67e22; }
    .main-header { background: linear-gradient(135deg, #2980b9, #27ae60); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); transition: background 0.5s ease; }
    .main-header.challenge { background: linear-gradient(135deg, #2c3e50, #c0392b, #8e44ad); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🎯 O-NET Math Pro <span style="font-size: 20px; background: #f1c40f; color: #333; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ป.6 Edition</span></h1>
    <p>ระบบสร้างข้อสอบ Mock Test เตรียมสอบ O-NET (ป.6) และสอบเข้า ม.1 พร้อมเฉลยละเอียดแบบ Step-by-Step</p>
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
FRUITS = ["แตงโม", "สับปะรด", "แอปเปิล", "สตรอว์เบอร์รี", "ส้ม", "มะม่วง"]

box_html = "<span style='display:inline-block; width:24px; height:24px; border:2px solid #c0392b; border-radius:4px; vertical-align:middle; background-color:#fff;'></span>"

def f_html(n, d, c="#2c3e50", b=True):
    if b:
        weight = "bold"
    else:
        weight = "normal"
    
    html_str = f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 4px;'>"
    html_str += f"<span style='border-bottom:2px solid {c}; padding:0 4px; font-weight:{weight}; color:{c};'>{n}</span>"
    html_str += f"<span style='padding:0 4px; font-weight:{weight}; color:{c};'>{d}</span>"
    html_str += f"</span>"
    return html_str

def get_vertical_fraction(num, den, color="#333", is_bold=True):
    if is_bold:
        weight = "bold"
    else:
        weight = "normal"
        
    html_str = f"""<span style="display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 6px; font-family:'Sarabun', sans-serif; white-space:nowrap;">"""
    html_str += f"""<span style="border-bottom:2px solid {color}; padding:2px 6px; font-weight:{weight}; color:{color};">{num}</span>"""
    html_str += f"""<span style="padding:2px 6px; font-weight:{weight}; color:{color};">{den}</span>"""
    html_str += f"""</span>"""
    return html_str

def generate_vertical_table_html(a, b, op, result="", is_key=False):
    if isinstance(a, int):
        a_str = f"{a:,}"
    else:
        a_str = str(a)
        
    if isinstance(b, int):
        b_str = f"{b:,}"
    else:
        b_str = str(b)
        
    if isinstance(result, int) and result != "":
        res_str = f"{result:,}"
    else:
        res_str = str(result)
        
    if is_key:
        ans_val = res_str
        border_ans = "border-bottom: 4px double #000;"
    else:
        ans_val = ""
        border_ans = ""
        
    html = f"""
    <div style='margin-left: 60px; display: block; font-family: "Sarabun", sans-serif; font-variant-numeric: tabular-nums; font-size: 26px; margin-top: 15px; margin-bottom: 15px;'>
        <table style='border-collapse: collapse; text-align: right;'>
            <tr>
                <td style='padding: 0 10px 0 0; border: none;'>{a_str}</td>
                <td rowspan='2' style='vertical-align: middle; text-align: left; padding: 0 0 0 15px; font-size: 28px; font-weight: bold; border: none; color: #333;'>{op}</td>
            </tr>
            <tr>
                <td style='padding: 5px 10px 5px 0; border: none; border-bottom: 2px solid #000;'>{b_str}</td>
            </tr>
            <tr>
                <td style='padding: 5px 10px 0 0; border: none; {border_ans} height: 35px;'>{ans_val}</td>
                <td style='border: none;'></td>
            </tr>
        </table>
    </div>
    """
    return html

def get_vertical_math(top_chars, bottom_chars, result_chars, operator="+"):
    max_len = max(len(top_chars), len(bottom_chars), len(result_chars))
    
    t_pad = [""] * (max_len - len(top_chars)) + top_chars
    b_pad = [""] * (max_len - len(bottom_chars)) + bottom_chars
    r_pad = [""] * (max_len - len(result_chars)) + result_chars
    
    html = "<table style='border-collapse:collapse; font-size:26px; font-weight:bold; text-align:center; margin:15px 0 15px 40px;'><tr>"
    for c in t_pad: 
        html += f"<td style='padding:5px 12px; width:35px;'>{c}</td>"
        
    html += f"<td rowspan='2' style='padding-left:20px; vertical-align:middle; font-size:28px; color:#2c3e50;'>{operator}</td></tr><tr>"
    
    for c in b_pad: 
        html += f"<td style='padding:5px 12px; width:35px; border-bottom:2px solid #333;'>{c}</td>"
        
    html += "</tr><tr>"
    
    for c in r_pad: 
        html += f"<td style='padding:5px 12px; width:35px; border-bottom:4px double #333;'>{c}</td>"
        
    html += "<td></td></tr></table>"
    return html

def lcm_multiple(*args):
    res = args[0]
    for i in args[1:]: 
        res = abs(res * i) // math.gcd(res, i)
    return res

def generate_short_division_html(nums, mode="ห.ร.ม."):
    factors = []
    current_nums = list(nums)
    steps_html = ""
    
    while True:
        found_factor = False
        if mode == "ห.ร.ม.":
            limit = min(current_nums)
        else:
            limit = max(current_nums)
            
        if limit < 2:
            break
            
        for i in range(2, int(limit) + 1):
            if mode == "ห.ร.ม.":
                if all(n % i == 0 for n in current_nums):
                    factors.append(i)
                    row_html = f"<tr><td style='text-align: right; padding-right: 10px; font-weight: bold; color: #c0392b;'>{i}</td>"
                    for idx, n in enumerate(current_nums):
                        if idx == 0:
                            border_left = "border-left: 2px solid #000;"
                        else:
                            border_left = ""
                        row_html += f"<td style='{border_left} border-bottom: 2px solid #000; padding: 5px 15px; text-align: center;'>{n}</td>"
                    row_html += "</tr>"
                    steps_html += row_html
                    current_nums = [n // i for n in current_nums]
                    found_factor = True
                    break
            else: # ค.ร.น.
                divisible_count = sum(1 for n in current_nums if n % i == 0)
                if divisible_count >= 2:
                    factors.append(i)
                    row_html = f"<tr><td style='text-align: right; padding-right: 10px; font-weight: bold; color: #c0392b;'>{i}</td>"
                    for idx, n in enumerate(current_nums):
                        if idx == 0:
                            border_left = "border-left: 2px solid #000;"
                        else:
                            border_left = ""
                        row_html += f"<td style='{border_left} border-bottom: 2px solid #000; padding: 5px 15px; text-align: center;'>{n}</td>"
                    row_html += "</tr>"
                    steps_html += row_html
                    
                    new_nums = []
                    for n in current_nums:
                        if n % i == 0:
                            new_nums.append(n // i)
                        else:
                            new_nums.append(n)
                    current_nums = new_nums
                    
                    found_factor = True
                    break
                    
        if not found_factor:
            break

    if not factors:
        if mode == "ห.ร.ม.": 
            return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ไม่มีจำนวนเฉพาะใดที่หาร {', '.join(map(str, nums))} ลงตัวพร้อมกัน<br><b>ดังนั้น ห.ร.ม. = 1</b></span>"
        else:
            ans = math.prod(nums)
            return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ไม่มีจำนวนเฉพาะใดที่หารเลขกลุ่มนี้ลงตัวตั้งแต่ 2 จำนวนขึ้นไป<br><b>ขั้นที่ 2:</b> ให้นำตัวเลขทั้งหมดมาคูณกันได้เลย<br><b>ดังนั้น ค.ร.น. = {' × '.join(map(str, nums))} = {ans:,}</b></span>"

    row_html = "<tr><td></td>"
    for idx, n in enumerate(current_nums):
        row_html += f"<td style='padding: 5px 15px; text-align: center;'>{n}</td>"
    row_html += "</tr>"
    steps_html += row_html
    table = f"<table style='margin: 10px 0; font-size: 20px; border-collapse: collapse; color: #333;'>{steps_html}</table>"

    if mode == "ห.ร.ม.":
        ans = math.prod(factors)
        calc_str = " × ".join(map(str, factors))
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br><b>ขั้นที่ 1:</b> หาจำนวนเฉพาะที่สามารถหารตัวเลข <b>ทั้งหมด</b> ลงตัวพร้อมกัน นำมาเป็นตัวหาร<br><b>ขั้นที่ 2:</b> หารไปเรื่อยๆ จนกว่าจะไม่มีตัวเลขใดหารลงตัวทั้งหมดแล้ว<br>{table}<br><b>ขั้นที่ 3:</b> การหา ห.ร.ม. ให้นำเฉพาะ <b>ตัวเลขด้านหน้าเครื่องหมายหารสั้น (แนวตั้ง)</b> มาคูณกัน<br><b>ดังนั้น ห.ร.ม. = {calc_str} = {ans:,}</b></span>"
    else:
        ans = math.prod(factors) * math.prod(current_nums)
        
        factors_and_rem = factors + [n for n in current_nums if n != 1]
        calc_str = " × ".join(map(str, factors_and_rem))
        
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br><b>ขั้นที่ 1:</b> หาจำนวนเฉพาะที่สามารถหารตัวเลขลงตัว <b>อย่างน้อย 2 จำนวนขึ้นไป</b><br><b>ขั้นที่ 2:</b> หารไปเรื่อยๆ (ตัวไหนหารไม่ลงตัวให้ดึงลงมาเหมือนเดิม) จนกว่าจะไม่มีตัวเลขใดหารลงตัวแล้ว<br>{table}<br><b>ขั้นที่ 3:</b> การหา ค.ร.น. ให้นำ <b>ตัวเลขด้านหน้าทั้งหมด และ เศษที่เหลือด้านล่างสุด (เป็นรูปตัว L)</b> มาคูณกัน (ไม่นับเลข 1)<br><b>ดังนั้น ค.ร.น. = {calc_str} = {ans:,}</b></span>"
    return sol


def draw_beakers_svg(v1_l, v1_ml, v2_l, v2_ml):
    def single_beaker(l, ml, name, color):
        tot = l * 1000 + ml
        if tot > 0:
            d_max = math.ceil(tot/1000)*1000
        else:
            d_max = 1000
            
        if d_max < 1000: 
            d_max = 1000
            
        h = 100
        w = 60
        fill_h = (tot / d_max) * h
        
        svg = f'<g>'
        svg += f'<rect x="0" y="{20+h-fill_h}" width="{w}" height="{fill_h}" fill="{color}" opacity="0.7"/>'
        svg += f'<path d="M0,20 L0,{20+h} Q0,{20+h+5} 5,{20+h+5} L{w-5},{20+h+5} Q{w},{20+h+5} {w},{20+h} L{w},20" fill="none" stroke="#34495e" stroke-width="3"/>'
        
        for i in range(1, 4):
            yy = 20 + h - (i * h / 4)
            svg += f'<line x1="0" y1="{yy}" x2="10" y2="{yy}" stroke="#34495e" stroke-width="2"/>'
            
        if l > 0:
            lbl = f"{l} ลิตร {ml} มล."
        else:
            lbl = f"{ml} มล."
            
        if ml == 0 and l > 0: 
            lbl = f"{l} ลิตร"
            
        svg += f'<text x="{w/2}" y="{h+45}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">{name}</text>'
        svg += f'<text x="{w/2}" y="{h+65}" font-family="Sarabun" font-size="14" fill="#e74c3c" font-weight="bold" text-anchor="middle">{lbl}</text>'
        svg += f'</g>'
        return svg

    svg1 = single_beaker(v1_l, v1_ml, "ถัง A", "#3498db")
    svg2 = single_beaker(v2_l, v2_ml, "ถัง B", "#1abc9c")
    
    full_svg = f'<div style="text-align:center; margin: 20px 0;"><svg width="300" height="200">'
    full_svg += f'<g transform="translate(50, 0)">{svg1}</g>'
    full_svg += f'<g transform="translate(190, 0)">{svg2}</g>'
    full_svg += '</svg></div>'
    return full_svg

def generate_unit_math_html(u_maj, u_min, v1_maj, v1_min, v2_maj, v2_min, op, multiplier):
    if op == "+":
        raw_min = v1_min + v2_min
        raw_maj = v1_maj + v2_maj
        
        carry = raw_min // multiplier
        fin_min = raw_min % multiplier
        fin_maj = raw_maj + carry
        
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        
        if carry > 0:
            html += f"<tr><td style='padding: 5px;'>{raw_maj:,}</td><td>{raw_min:,}</td><td></td></tr>"
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td style='font-size: 16px; text-align: left; padding-left: 10px;'>(ทด <b style='color:red;'>{carry}</b> {u_maj})</td></tr>"
        else:
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        
        if fin_min > 0:
            ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}"
        else:
            ans_str = f"{fin_maj:,} {u_maj}"
            
        return html, ans_str
    else: 
        if v1_min < v2_min:
            is_borrow = True
        else:
            is_borrow = False
            
        if is_borrow:
            c_v1_maj = v1_maj - 1
            c_v1_min = v1_min + multiplier
        else:
            c_v1_maj = v1_maj
            c_v1_min = v1_min
            
        fin_maj = c_v1_maj - v2_maj
        fin_min = c_v1_min - v2_min
        
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        
        if is_borrow:
            html += f"<tr style='color: #e74c3c; font-size: 18px; font-weight: bold;'><td>{c_v1_maj:,}</td><td>{c_v1_min:,}</td><td></td></tr>"
            html += f"<tr><td style='padding: 5px; text-decoration: line-through;'>{v1_maj:,}</td><td style='text-decoration: line-through;'>{v1_min:,}</td><td></td></tr>"
        else:
            html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
            
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        
        if fin_min > 0:
            ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}"
        else:
            ans_str = f"{fin_maj:,} {u_maj}"
            
        if fin_maj <= 0: 
            ans_str = f"{fin_min:,} {u_min}"
            
        return html, ans_str

# ==========================================
# 2. ฐานข้อมูลหัวข้อข้อสอบสำหรับ O-NET ป.6
# ==========================================
onet_p6_topics = [
    "โจทย์ปัญหา ห.ร.ม. (แบ่งของ)",
    "โจทย์ปัญหา ค.ร.น. (เวลา/จุดนัดพบ)",
    "โจทย์ปัญหาเศษส่วนประยุกต์",
    "ร้อยละ เปอร์เซ็นต์ (กำไร/ลดราคา)",
    "สมการและโจทย์ปัญหาสมการ",
    "แบบรูปและความสัมพันธ์ (Patterns)",
    "สถิติและค่าเฉลี่ย",
    "ปริมาตรและความจุ",
    "การแปลงหน่วยและเปรียบเทียบ"
]

# ==========================================
# 3. Logic Generator 
# ==========================================
def generate_questions_logic(level, sub_t, num_q, is_challenge):
    questions = []
    seen = set()

    for _ in range(num_q):
        q = ""
        sol = ""
        attempts = 0
        
        while attempts < 500:
            attempts += 1
            if sub_t == "🌟 สุ่มรวมทุกแนว (ป.6 O-NET)":
                actual_sub_t = random.choice(onet_p6_topics)
            else:
                actual_sub_t = sub_t
                
            name = random.choice(NAMES)

            # ---------------------------------------------------------
            if actual_sub_t == "โจทย์ปัญหา ห.ร.ม. (แบ่งของ)":
                scenario = random.choice(["fruit", "wire", "student"])
                
                if scenario == "fruit":
                    f1 = random.choice(FRUITS)
                    f2 = random.choice(FRUITS)
                    while f1 == f2:
                        f2 = random.choice(FRUITS)
                        
                    if is_challenge:
                        gcd_val = random.randint(15, 30)
                    else:
                        gcd_val = random.randint(5, 15)
                        
                    m1 = random.randint(3, 7)
                    m2 = random.randint(4, 9)
                    while m1 == m2: 
                        m2 = random.randint(4, 9)
                    
                    qty1 = gcd_val * m1
                    qty2 = gcd_val * m2
                    total_baskets = m1 + m2
                    
                    q = f"<b>{name}</b> มี{f1} <b>{qty1} ผล</b> และ{f2} <b>{qty2} ผล</b> ต้องการแบ่งผลไม้ใส่ตะกร้า <br>โดยแต่ละตะกร้าต้องมีผลไม้ชนิดเดียวกัน จำนวนเท่าๆ กัน และให้ได้ <b>'จำนวนผลไม้ต่อตะกร้ามากที่สุด'</b> โดยไม่มีเศษเหลือ <br>จะต้องใช้ตะกร้าทั้งหมดกี่ใบ?"
                    
                    div_table = generate_short_division_html([qty1, qty2], mode="ห.ร.ม.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ห.ร.ม.):</b><br>
                    โจทย์ที่มีคำว่า "แบ่งให้เท่าๆ กัน และได้จำนวนมากที่สุด" คือการหา <b>ห.ร.ม. (หารร่วมมาก)</b><br>
                    <b>ขั้นตอนที่ 1: หาจำนวนผลไม้ที่มากที่สุดต่อ 1 ตะกร้า (หา ห.ร.ม.)</b><br>
                    👉 นำจำนวนผลไม้ {qty1} และ {qty2} มาตั้งหารสั้น<br>
                    {div_table}
                    👉 ตัวเลข ห.ร.ม. ที่ได้คือ <b>{gcd_val}</b> (แสดงว่าต้องจัดตะกร้าละ {gcd_val} ผล)<br>
                    <b>ขั้นตอนที่ 2: หาจำนวนตะกร้าของผลไม้แต่ละชนิด</b><br>
                    👉 นำจำนวนผลไม้ตั้ง หารด้วยจำนวนต่อตะกร้า (หรือดูจากผลลัพธ์เศษที่เหลือด้านล่างสุดของการหารสั้นได้เลย!)<br>
                    👉 {f1} {qty1} ผล จัดตะกร้าละ {gcd_val} ผล จะได้: {qty1} ÷ {gcd_val} = <b>{m1} ใบ</b><br>
                    👉 {f2} {qty2} ผล จัดตะกร้าละ {gcd_val} ผล จะได้: {qty2} ÷ {gcd_val} = <b>{m2} ใบ</b><br>
                    <b>ขั้นตอนที่ 3: หาจำนวนตะกร้าทั้งหมด</b><br>
                    👉 นำจำนวนตะกร้ามาบวกกัน: {m1} + {m2} = <b>{total_baskets} ใบ</b><br>
                    <b>ตอบ: {total_baskets} ใบ</b></span>"""
                    
                elif scenario == "wire":
                    if is_challenge:
                        gcd_val = random.randint(12, 25)
                        m1 = random.randint(5, 9)
                        m2 = random.randint(4, 8)
                        m3 = random.randint(3, 7)
                        while m1 == m2 or m1 == m3 or m2 == m3:
                            m3 = random.randint(3, 7)
                            m2 = random.randint(4, 8)
                    else:
                        gcd_val = random.randint(4, 12)
                        m1 = random.randint(3, 6)
                        m2 = random.randint(2, 5)
                        m3 = random.randint(4, 7)
                        while m1 == m2 or m1 == m3 or m2 == m3:
                            m2 = random.randint(2, 5)
                            m3 = random.randint(4, 7)
                            
                    l1 = gcd_val * m1
                    l2 = gcd_val * m2
                    l3 = gcd_val * m3
                    total_pieces = m1 + m2 + m3
                    
                    q = f"ช่างก่อสร้างมีลวดอยู่ 3 เส้น ยาว <b>{l1} เซนติเมตร, {l2} เซนติเมตร, และ {l3} เซนติเมตร</b> ตามลำดับ <br>ต้องการตัดลวดทั้งสามเส้นให้เป็นท่อนสั้นๆ ยาวเท่าๆ กัน โดยให้ได้ <b>'ความยาวมากที่สุด'</b> และไม่ให้เหลือเศษ <br>ลวดที่ถูกตัดแต่ละท่อนจะมีความยาวเท่าไร และจะได้ลวดทั้งหมดกี่ท่อน?"
                    
                    div_table = generate_short_division_html([l1, l2, l3], mode="ห.ร.ม.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ห.ร.ม.):</b><br>
                    โจทย์การตัดแบ่งสิ่งของให้ยาวที่สุดและเท่าๆ กัน คือการหา <b>ห.ร.ม. (หารร่วมมาก)</b><br>
                    <b>ขั้นตอนที่ 1: หาความยาวของลวดต่อท่อน (หา ห.ร.ม.)</b><br>
                    👉 นำความยาวของลวดทั้งสามเส้น {l1}, {l2}, และ {l3} มาตั้งหารสั้น<br>
                    {div_table}
                    👉 ตัวเลข ห.ร.ม. ที่ได้คือ <b>{gcd_val}</b> (แสดงว่าลวดแต่ละท่อนจะยาว {gcd_val} ซม.)<br>
                    <b>ขั้นตอนที่ 2: หาจำนวนท่อนทั้งหมด</b><br>
                    👉 ดูจากผลลัพธ์เศษด้านล่างสุดของการหารสั้น นำมาบวกกันได้เลย<br>
                    👉 เส้นที่ 1 ได้ {m1} ท่อน, เส้นที่ 2 ได้ {m2} ท่อน, เส้นที่ 3 ได้ {m3} ท่อน<br>
                    👉 นำมาบวกกัน: {m1} + {m2} + {m3} = <b>{total_pieces} ท่อน</b><br>
                    <b>ตอบ: ยาวท่อนละ {gcd_val} เซนติเมตร และได้ทั้งหมด {total_pieces} ท่อน</b></span>"""
                    
                else: # student
                    if is_challenge:
                        gcd_val = random.randint(8, 15)
                        m1 = random.randint(6, 12)
                        m2 = random.randint(5, 11)
                    else:
                        gcd_val = random.randint(4, 9)
                        m1 = random.randint(5, 10)
                        m2 = random.randint(4, 9)
                        
                    while m1 == m2: 
                        m2 = random.randint(4, 10)
                        
                    boy = gcd_val * m1
                    girl = gcd_val * m2
                    total_groups = m1 + m2
                    
                    q = f"คุณครูมีนักเรียนชาย <b>{boy} คน</b> และนักเรียนหญิง <b>{girl} คน</b> ต้องการจัดกลุ่มนักเรียน <br>โดยแต่ละกลุ่มต้องมีนักเรียนเพศเดียวกันเท่านั้น มีจำนวนคนเท่าๆ กัน และให้ได้ <b>'นักเรียนต่อกลุ่มมากที่สุด'</b> <br>จะจัดนักเรียนได้กลุ่มละกี่คน และจัดได้ทั้งหมดกี่กลุ่ม?"
                    
                    div_table = generate_short_division_html([boy, girl], mode="ห.ร.ม.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ห.ร.ม.):</b><br>
                    การจัดกลุ่มให้เท่ากันและได้สมาชิกมากที่สุด คือการหา <b>ห.ร.ม. (หารร่วมมาก)</b><br>
                    <b>ขั้นตอนที่ 1: หาจำนวนคนในแต่ละกลุ่ม (หา ห.ร.ม.)</b><br>
                    👉 นำจำนวนนักเรียนชายและหญิงมาตั้งหารสั้น<br>
                    {div_table}
                    👉 ตัวเลข ห.ร.ม. ที่ได้คือ <b>{gcd_val}</b> (แสดงว่าจะได้กลุ่มละ {gcd_val} คน)<br>
                    <b>ขั้นตอนที่ 2: หาจำนวนกลุ่มที่ได้</b><br>
                    👉 ดูจากตัวเลขด้านล่างสุดของตารางหารสั้น<br>
                    👉 นักเรียนชายแบ่งได้ {m1} กลุ่ม, นักเรียนหญิงแบ่งได้ {m2} กลุ่ม<br>
                    👉 นำจำนวนกลุ่มมาบวกกัน: {m1} + {m2} = <b>{total_groups} กลุ่ม</b><br>
                    <b>ตอบ: จัดได้กลุ่มละ {gcd_val} คน และได้ทั้งหมด {total_groups} กลุ่ม</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหา ค.ร.น. (เวลา/จุดนัดพบ)":
                scenario = random.choice(["clock", "bus", "run"])
                
                if scenario == "clock":
                    items_list = ["นาฬิกาปลุก", "ระฆัง", "สัญญาณไฟ"]
                    item_word = random.choice(items_list)
                    time_choices = [10, 12, 15, 20, 30, 45, 60]
                    
                    if is_challenge:
                        l1 = random.choice(time_choices)
                        l2 = random.choice(time_choices)
                        while l2 == l1:
                            l2 = random.choice(time_choices)
                        l3 = random.choice(time_choices)
                        while l3 == l1 or l3 == l2:
                            l3 = random.choice(time_choices)
                        l4 = random.choice(time_choices)
                        while l4 == l1 or l4 == l2 or l4 == l3:
                            l4 = random.choice(time_choices)
                            
                        lcm = lcm_multiple(l1, l2, l3, l4)
                        ans_min = lcm // 60
                        ans_sec = lcm % 60
                        
                        if ans_sec == 0:
                            text_ans = f"{ans_min} นาที"
                        else:
                            text_ans = f"{ans_min} นาที {ans_sec} วินาที"
                            
                        q = f"<b>{item_word} 4 ชิ้น</b> ทำงานด้วยจังหวะที่ต่างกัน ดังนี้:<br>ชิ้นที่ 1 ดังทุกๆ {l1} วินาที, ชิ้นที่ 2 ดังทุกๆ {l2} วินาที, ชิ้นที่ 3 ดังทุกๆ {l3} วินาที, และชิ้นที่ 4 ดังทุกๆ {l4} วินาที <br>ถ้าเพิ่งดังพร้อมกันไป อีกกี่นาทีข้างหน้าจึงจะดังพร้อมกันอีกครั้ง?"
                        
                        div_table = generate_short_division_html([l1, l2, l3, l4], mode="ค.ร.น.")
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                        โจทย์ที่มีคำว่า "เกิดขึ้นพร้อมกันอีกครั้ง" ให้ใช้การหา <b>ค.ร.น. (คูณร่วมน้อย)</b><br>
                        <b>ขั้นตอนที่ 1: ตั้งหารสั้นเพื่อหา ค.ร.น.</b><br>
                        👉 นำตัวเลขรอบเวลาทั้ง 4 ชิ้น มาตั้งหารสั้น<br>
                        {div_table}
                        👉 จะได้รอบเวลาที่ลงตัวพร้อมกันคือ <b>{lcm} วินาที</b><br>
                        <b>ขั้นตอนที่ 2: แปลงหน่วยวินาทีเป็นนาทีและวินาที</b><br>
                        👉 1 นาที มี 60 วินาที ให้นำ {lcm} ÷ 60<br>
                        👉 จะได้ผลลัพธ์เท่ากับ <b>{text_ans}</b> พอดี<br>
                        <b>ตอบ: {text_ans}</b></span>"""
                    else:
                        l1 = random.choice(time_choices)
                        l2 = random.choice(time_choices)
                        while l2 == l1:
                            l2 = random.choice(time_choices)
                        l3 = random.choice(time_choices)
                        while l3 == l1 or l3 == l2:
                            l3 = random.choice(time_choices)
                            
                        lcm = lcm_multiple(l1, l2, l3)
                        
                        q = f"{item_word} 3 ชิ้น ทำงานด้วยจังหวะที่ต่างกัน ชิ้นแรกดังทุกๆ {l1} นาที, ชิ้นที่สอง {l2} นาที และชิ้นที่สาม {l3} นาที <br>ถ้าเพิ่งดังพร้อมกันไป อีกกี่นาทีข้างหน้าจึงจะดังพร้อมกันอีกครั้ง?"
                        
                        div_table = generate_short_division_html([l1, l2, l3], mode="ค.ร.น.")
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                        โจทย์ที่ถามหาจุดที่ "เกิดขึ้นพร้อมกันอีกครั้ง" คือการหา <b>ค.ร.น. (คูณร่วมน้อย)</b><br>
                        <b>ขั้นตอนที่ 1: ตั้งหารสั้นหา ค.ร.น.</b><br>
                        👉 นำรอบเวลาทั้งหมด ({l1}, {l2}, และ {l3}) มาตั้งหารสั้น<br>
                        {div_table}
                        <b>ขั้นตอนที่ 2: สรุปผล ค.ร.น.</b><br>
                        👉 เมื่อนำตัวเลขด้านหน้าและเศษด้านล่างมาคูณกันทั้งหมด จะได้ผลลัพธ์เท่ากับ <b>{lcm}</b><br>
                        👉 แสดงว่าอีก {lcm} นาที วงจรรอบเวลาของทั้ง 3 ชิ้นจะวนมาตรงกันพอดีเป๊ะ<br>
                        <b>ตอบ: อีก {lcm} นาที</b></span>"""
                
                elif scenario == "bus":
                    start_h = random.randint(6, 10)
                    time_choices = [15, 20, 25, 30, 40, 45, 60]
                    t1, t2, t3 = random.sample(time_choices, 3)
                    lcm = lcm_multiple(t1, t2, t3)
                    
                    add_h = lcm // 60
                    add_m = lcm % 60
                    ans_h = start_h + add_h
                    ans_m = add_m
                    
                    q = f"สถานีขนส่งแห่งหนึ่ง ปล่อยรถโดยสาร 3 สาย <br>สาย A ออกทุกๆ <b>{t1} นาที</b>, สาย B ออกทุกๆ <b>{t2} นาที</b>, และสาย C ออกทุกๆ <b>{t3} นาที</b><br>ถ้ารถทั้ง 3 สายเพิ่งออกเดินทางพร้อมกันตอนเวลา <b>0{start_h}:00 น.</b> รถทั้ง 3 สายจะออกเดินทางพร้อมกันอีกครั้งเวลาใด?"
                    
                    div_table = generate_short_division_html([t1, t2, t3], mode="ค.ร.น.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                    <b>ขั้นตอนที่ 1: หาเวลาร่วมที่รถจะออกพร้อมกัน (หา ค.ร.น.)</b><br>
                    👉 นำรอบเวลาการปล่อยรถ {t1}, {t2}, และ {t3} นาที มาตั้งหารสั้น<br>
                    {div_table}
                    👉 ค.ร.น. คือ <b>{lcm} นาที</b> แสดงว่าต้องรออีก {lcm} นาที รถถึงจะออกพร้อมกัน<br>
                    <b>ขั้นตอนที่ 2: แปลงหน่วยเป็นชั่วโมงและนาที</b><br>
                    👉 นำ {lcm} นาที ÷ 60 จะได้ <b>{add_h} ชั่วโมง {add_m} นาที</b><br>
                    <b>ขั้นตอนที่ 3: คำนวณเวลาที่หน้าปัดนาฬิกา</b><br>
                    👉 เริ่มต้น 0{start_h}:00 น. บวกไปอีก {add_h} ชั่วโมง {add_m} นาที<br>
                    👉 จะได้เวลา <b>{ans_h:02d}:{ans_m:02d} น.</b><br>
                    <b>ตอบ: เวลา {ans_h:02d}:{ans_m:02d} น.</b></span>"""
                    
                else: # run
                    n1, n2 = random.sample(NAMES, 2)
                    if is_challenge:
                        n3 = random.choice([n for n in NAMES if n != n1 and n != n2])
                        time_choices = [8, 12, 15, 20, 24]
                        t1, t2, t3 = random.sample(time_choices, 3)
                        lcm = lcm_multiple(t1, t2, t3)
                        
                        q = f"<b>{n1}</b>, <b>{n2}</b>, และ <b>{n3}</b> วิ่งรอบสนามแข่ง 1 รอบ ใช้เวลา <b>{t1} นาที</b>, <b>{t2} นาที</b>, และ <b>{t3} นาที</b> ตามลำดับ<br>ถ้าทั้งสามคนออกสตาร์ทพร้อมกัน พวกเขาจะวิ่งมาเจอกันที่ 'จุดเริ่มต้น' พร้อมกันอีกครั้งในอีกกี่นาที?"
                        div_table = generate_short_division_html([t1, t2, t3], mode="ค.ร.น.")
                    else:
                        time_choices = [4, 6, 8, 10, 12, 15]
                        t1, t2 = random.sample(time_choices, 2)
                        lcm = lcm_multiple(t1, t2)
                        
                        q = f"<b>{n1}</b> และ <b>{n2}</b> วิ่งรอบสนามแข่ง 1 รอบ ใช้เวลา <b>{t1} นาที</b> และ <b>{t2} นาที</b> ตามลำดับ<br>ถ้าทั้งสองคนออกสตาร์ทพร้อมกัน พวกเขาจะวิ่งมาเจอกันที่ 'จุดเริ่มต้น' อีกครั้งในอีกกี่นาที?"
                        div_table = generate_short_division_html([t1, t2], mode="ค.ร.น.")
                        
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                    โจทย์การวิ่งวนรอบสนามแล้วกลับมาเจอกันที่เดิม คือโจทย์ <b>ค.ร.น. (ตัวคูณร่วมน้อย)</b> คลาสสิก<br>
                    <b>ขั้นตอนที่ 1: ตั้งหารสั้นเพื่อหาจุดร่วม</b><br>
                    👉 นำเวลาการวิ่งต่อ 1 รอบของแต่ละคนมาตั้งหารสั้น<br>
                    {div_table}
                    <b>ขั้นตอนที่ 2: สรุปผล</b><br>
                    👉 ค.ร.น. ที่คำนวณได้คือ <b>{lcm} นาที</b><br>
                    👉 นั่นหมายความว่า ต้องใช้เวลาวิ่งวนไปเรื่อยๆ จนครบ {lcm} นาที ทุกคนจึงจะมาครบรอบที่จุดสตาร์ทพร้อมกันพอดี<br>
                    <b>ตอบ: อีก {lcm} นาที</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาเศษส่วนประยุกต์":
                scenario = random.choice(["book", "money", "pole"])
                
                if scenario == "book":
                    if is_challenge:
                        Y = random.randint(10, 30)
                        R2 = 2 * Y
                        X = random.randint(10, 30)
                        while (R2 + X) % 2 != 0: 
                            X += 1
                        R1 = (R2 + X) * 3 // 2
                        Total = R1 * 4 // 3
                        
                        f1_4 = get_vertical_fraction(1, 4)
                        f1_3 = get_vertical_fraction(1, 3)
                        f1_2 = get_vertical_fraction(1, 2)
                        
                        f1_4_s = get_vertical_fraction(1, 4, color="#2c3e50", is_bold=False)
                        f1_3_s = get_vertical_fraction(1, 3, color="#2c3e50", is_bold=False)
                        f1_2_s = get_vertical_fraction(1, 2, color="#2c3e50", is_bold=False)
                        f2_3_s = get_vertical_fraction(2, 3, color="#2c3e50", is_bold=False)
                        f3_4_s = get_vertical_fraction(3, 4, color="#2c3e50", is_bold=False)
                        
                        q = f"<b>{name}</b> อ่านหนังสือเล่มหนึ่ง <b>วันแรกอ่านไป {f1_4} ของเล่ม</b><br><b>วันที่สองอ่านไป {f1_3} ของหน้าที่เหลือ</b> และอ่านเพิ่มอีก <b>{X} หน้า</b><br><b>วันที่สามอ่านไป {f1_2} ของหน้าที่เหลือ</b> และอ่านเพิ่มอีก <b>{Y} หน้า</b> ปรากฏว่าอ่านจบเล่มพอดี!<br>จงหาว่าหนังสือเล่มนี้มีทั้งหมดกี่หน้า?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (คิดย้อนกลับแบบสมการเศษส่วน):</b><br>
                        <b>วันที่ 3:</b> อ่านไป {f1_2_s} แล้วอ่านอีก {Y} หน้าจนจบ<br>
                        👉 แสดงว่า {Y} หน้าที่เหลือ คืออีกครึ่งหนึ่งพอดี ➔ ตั้งสมการ: 🔲 ÷ 2 = {Y}<br>
                        👉 นำ 2 ไปคูณย้ายข้าง: 🔲 = {Y} <b style='color:red;'>× 2</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด (หน้าก่อนอ่านวันที่ 3): 🔲 = {R2} หน้า</b><br><br>
                        
                        <b>วันที่ 2:</b> อ่านไป {f1_3_s} ของที่เหลือ + {X} หน้า ทำให้เหลือ {R2} หน้า<br>
                        👉 ตั้งสมการ: ถ้าอ่านไป {f1_3_s} ส่วนที่เหลือคือ {f2_3_s}<br>
                        👉 ({f2_3_s} × 🔲) - {X} = {R2}<br>
                        👉 ย้าย {X} ไปบวก: ({f2_3_s} × 🔲) = {R2} <b style='color:red;'>+ {X}</b> = {R2+X}<br>
                        👉 ย้าย 2/3 ไปอีกฝั่ง (กลับเศษเป็นส่วน): 🔲 = {R2+X} <b style='color:red;'>× 3 ÷ 2</b><br>
                        👉 คำนวณ: ({R2+X} ÷ 2) × 3 = {int((R2+X)/2)} × 3 = <b>{R1}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด (หน้าก่อนอ่านวันที่ 2): 🔲 = {R1} หน้า</b><br><br>
                        
                        <b>วันที่ 1:</b> อ่านไป {f1_4_s} ของทั้งเล่ม ทำให้เหลือ {R1} หน้า<br>
                        👉 ตั้งสมการ: ถ้าอ่านไป {f1_4_s} ส่วนที่เหลือคือ {f3_4_s} ของทั้งเล่ม<br>
                        👉 {f3_4_s} × 🔲(ทั้งหมด) = {R1}<br>
                        👉 ย้าย 3/4 ไปอีกฝั่ง (กลับเศษเป็นส่วน): 🔲 = {R1} <b style='color:red;'>× 4 ÷ 3</b><br>
                        👉 คำนวณ: ({R1} ÷ 3) × 4 = {int(R1/3)} × 4 = <b>{Total}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด (หน้าทั้งหมด): 🔲 = {Total} หน้า</b><br>
                        <b>ตอบ: {Total} หน้า</b></span>"""
                    else:
                        den = random.choice([4, 5, 6, 8, 10])
                        num = random.randint(1, den-2)
                        total_money = random.randint(10, 50) * den
                        ans_rem = total_money - int((total_money/den)*num)
                        
                        frac_html = get_vertical_fraction(num, den)
                        
                        q = f"<b>{name}</b> มีเงิน <b>{total_money} บาท</b> นำไปซื้ออุปกรณ์การเรียน <b>{frac_html}</b> ของเงินทั้งหมดที่มี <br>เขาจะเหลือเงินกี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แก้สมการเศษส่วน):</b><br>
                        <b>ขั้นตอนที่ 1: หาจำนวนเงินที่ใช้ไป</b><br>
                        👉 คำว่า "ของ" ในทางคณิตศาสตร์คือเครื่องหมาย "คูณ (×)"<br>
                        👉 ตั้งสมการ: เงินที่ใช้ = {total_money} <b style='color:red;'>× {num} ÷ {den}</b><br>
                        👉 ทำการหารก่อนเพื่อตัดทอนตัวเลข: {total_money} ÷ {den} = <b>{total_money//den}</b><br>
                        👉 จากนั้นนำผลลัพธ์ไปคูณ: {total_money//den} × {num} = <b>{int((total_money/den)*num)} บาท</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: เงินที่ใช้ไป = {int((total_money/den)*num)} บาท</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณเงินที่เหลือ</b><br>
                        👉 สมการ: เงินที่เหลือ = เงินตอนแรก - เงินที่ใช้ไป<br>
                        👉 แทนค่า: เงินที่เหลือ = {total_money} - {int((total_money/den)*num)} = <b>{ans_rem}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: เงินที่เหลือ = {ans_rem} บาท</b><br>
                        <b>ตอบ: {ans_rem} บาท</b></span>"""
                        
                elif scenario == "money":
                    # ซื้อของสองอย่าง หาเงินที่เหลือ
                    total = random.choice([1200, 2400, 3600, 4800])
                    # Fix fractions like 1/3 and 1/4
                    den1, den2 = 3, 4
                    num1, num2 = 1, 1
                    
                    spent1 = (total * num1) // den1
                    spent2 = (total * num2) // den2
                    rem = total - (spent1 + spent2)
                    
                    f1 = get_vertical_fraction(num1, den1)
                    f2 = get_vertical_fraction(num2, den2)
                    
                    q = f"<b>{name}</b> ได้รับเงินเดือน <b>{total:,} บาท</b><br>เขานำไปจ่ายค่าอาหาร <b>{f1} ของเงินเดือนทั้งหมด</b> และจ่ายค่าที่พัก <b>{f2} ของเงินเดือนทั้งหมด</b><br>เขาจะเหลือเงินเก็บกี่บาท?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาเงินที่จ่ายค่าอาหาร</b><br>
                    👉 คำนวณ: {total:,} <b style='color:red;'>× {num1} ÷ {den1}</b> = <b>{spent1:,} บาท</b><br>
                    <b>ขั้นตอนที่ 2: หาเงินที่จ่ายค่าที่พัก</b><br>
                    👉 (โจทย์บอกว่าของเงินเดือนทั้งหมด ไม่ใช่ของที่เหลือ)<br>
                    👉 คำนวณ: {total:,} <b style='color:red;'>× {num2} ÷ {den2}</b> = <b>{spent2:,} บาท</b><br>
                    <b>ขั้นตอนที่ 3: หายอดเงินคงเหลือ</b><br>
                    👉 นำรายจ่ายมารวมกัน: {spent1:,} + {spent2:,} = <b>{spent1+spent2:,} บาท</b><br>
                    👉 นำเงินเดือนหักลบรายจ่าย: {total:,} - {spent1+spent2:,} = <b>{rem:,} บาท</b><br>
                    <b>ตอบ: {rem:,} บาท</b></span>"""
                    
                else: # pole
                    # เสาปักในโคลน
                    tot_m = random.choice([12, 15, 18, 20, 24])
                    f_mud = get_vertical_fraction(1, 3)
                    f_water = get_vertical_fraction(1, 4)
                    
                    mud_part = tot_m // 3
                    water_part = tot_m // 4
                    air_part = tot_m - (mud_part + water_part)
                    
                    if is_challenge:
                        q = f"เสาไม้ต้นหนึ่งปักอยู่ในสระบัว ส่วนที่จมอยู่ในโคลนคิดเป็น <b>{f_mud} ของความยาวทั้งต้น</b><br>ส่วนที่แช่อยู่ในน้ำคิดเป็น <b>{f_water} ของความยาวทั้งต้น</b><br>และมีส่วนที่โผล่พ้นน้ำขึ้นมา <b>{air_part} เมตร</b> จงหาว่าเสาไม้ต้นนี้ 'ยาวทั้งหมด' กี่เมตร?"
                        
                        f_sum_1 = get_vertical_fraction("1×4", "3×4", color="#2c3e50", is_bold=False)
                        f_sum_2 = get_vertical_fraction("1×3", "4×3", color="#2c3e50", is_bold=False)
                        f_total_sub = get_vertical_fraction("7", "12", color="#2c3e50", is_bold=False)
                        f_rem = get_vertical_fraction("5", "12", color="#2c3e50", is_bold=False)
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แก้สมการเศษส่วนแบบย้อนกลับ):</b><br>
                        <b>ขั้นตอนที่ 1: หาว่าเสาจมไปแล้วกี่ส่วนของต้น</b><br>
                        👉 นำส่วนโคลนและน้ำมาบวกกัน: {f_mud} + {f_water}<br>
                        👉 ทำส่วนให้เท่ากัน (ค.ร.น. คือ 12): {f_sum_1} + {f_sum_2} = <b>{f_total_sub} ของทั้งต้น</b><br>
                        <b>ขั้นตอนที่ 2: หาเศษส่วนของส่วนที่โผล่พ้นน้ำ</b><br>
                        👉 ความยาวทั้งต้นคือ 12/12 หักส่วนที่จมลงไป 7/12<br>
                        👉 ส่วนที่โผล่พ้นน้ำ = 12/12 - 7/12 = <b>{f_rem} ของทั้งต้น</b><br>
                        <b>ขั้นตอนที่ 3: ตั้งสมการหาความยาวทั้งหมด</b><br>
                        👉 โจทย์บอกว่าส่วนที่โผล่พ้นน้ำจริงๆ ยาว {air_part} เมตร<br>
                        👉 ตั้งสมการ: {f_rem} × 🔲(ความยาวเต็ม) = {air_part}<br>
                        👉 ย้ายข้างกลับเศษเป็นส่วน: 🔲 = {air_part} <b style='color:red;'>× 12 ÷ 5</b><br>
                        👉 คำนวณ: ({air_part} ÷ 5) × 12 = {int(air_part/5)} × 12 = <b>{tot_m} เมตร</b><br>
                        <b>ตอบ: {tot_m} เมตร</b></span>"""
                    else:
                        q = f"เสาไม้ต้นหนึ่งยาว <b>{tot_m} เมตร</b> ปักอยู่ในสระบัว<br>ส่วนที่จมอยู่ในโคลนคิดเป็น <b>{f_mud} ของความยาวทั้งต้น</b><br>ส่วนที่แช่อยู่ในน้ำคิดเป็น <b>{f_water} ของความยาวทั้งต้น</b><br>จงหาว่าเสาไม้มีส่วนที่โผล่พ้นน้ำขึ้นมากี่เมตร?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: หาความยาวส่วนที่จมโคลน</b><br>
                        👉 คำนวณ: {tot_m} <b style='color:red;'>× 1 ÷ 3</b> = <b>{mud_part} เมตร</b><br>
                        <b>ขั้นตอนที่ 2: หาความยาวส่วนที่แช่น้ำ</b><br>
                        👉 (โจทย์บอกว่าของทั้งต้น ไม่ใช่ของที่เหลือ)<br>
                        👉 คำนวณ: {tot_m} <b style='color:red;'>× 1 ÷ 4</b> = <b>{water_part} เมตร</b><br>
                        <b>ขั้นตอนที่ 3: หาความยาวส่วนที่โผล่พ้นน้ำ</b><br>
                        👉 นำความยาวเต็ม ลบด้วยส่วนที่จมไปแล้ว: {tot_m} - ({mud_part} + {water_part}) = <b>{air_part} เมตร</b><br>
                        <b>ตอบ: {air_part} เมตร</b></span>"""

            elif actual_sub_t == "ร้อยละ เปอร์เซ็นต์ (กำไร/ลดราคา)":
                scenario = random.choice(["discount", "exam", "interest"])
                
                if scenario == "discount":
                    if is_challenge:
                        discount_choices = [10, 15, 20, 25, 30]
                        discount_pct = random.choice(discount_choices)
                        sell_price = random.randint(50, 200) * 10
                        original_price = int(sell_price * 100 / (100 - discount_pct))
                        
                        while original_price * (100 - discount_pct) / 100 != sell_price:
                            sell_price = random.randint(50, 200) * 10
                            original_price = int(sell_price * 100 / (100 - discount_pct))
                            
                        q = f"ร้านค้าติดป้ายลดราคาสินค้า <b>{discount_pct}%</b> ทำให้ <b>{name}</b> ซื้อสินค้าชิ้นนี้มาในราคา <b>{sell_price:,} บาท</b> <br>จงหาว่าร้านค้า 'ติดป้ายราคาก่อนลด' ไว้ที่กี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (คิดย้อนกลับเทียบร้อยละ):</b><br>
                        ให้ 🔲 แทน "ราคาป้ายเดิม" (ซึ่งก็คือ 100%)<br>
                        <b>ขั้นตอนที่ 1: ตีความหมายเปอร์เซ็นต์ลดราคา</b><br>
                        👉 ลดราคา {discount_pct}% หมายความว่า เราจ่ายเงินซื้อจริงเพียง 100 - {discount_pct} = <b>{100 - discount_pct}%</b> ของราคาป้าย<br>
                        <b>ขั้นตอนที่ 2: ตั้งสมการเพื่อหาราคาเดิม</b><br>
                        👉 สมการ: (เปอร์เซ็นต์ที่จ่ายจริง ÷ 100) × ราคาป้าย = ราคาที่จ่าย<br>
                        👉 แทนค่า: ({100 - discount_pct} ÷ 100) × 🔲 = {sell_price:,}<br>
                        <b>ขั้นตอนที่ 3: ใช้คุณสมบัติการย้ายข้างสมการ</b><br>
                        👉 ย้ายฝั่งเปลี่ยนหารเป็นคูณ เปลี่ยนคูณเป็นหาร: <br>
                        &nbsp;&nbsp;&nbsp; 🔲 = {sell_price:,} <b style='color:red;'>× 100 ÷ {100 - discount_pct}</b><br>
                        👉 ทำการหารตัดทอนก่อน: {sell_price:,} ÷ {100 - discount_pct} = <b>{sell_price // (100 - discount_pct):,}</b><br>
                        👉 นำไปคูณ 100: {sell_price // (100 - discount_pct):,} × 100 = <b>{original_price:,}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: 🔲 (ราคาป้าย) = {original_price:,} บาท</b><br>
                        <b>ตอบ: {original_price:,} บาท</b></span>"""
                    else:
                        cost = random.randint(10, 50) * 100
                        profit_choices = [10, 15, 20, 25, 30, 40, 50]
                        profit_pct = random.choice(profit_choices)
                        profit_baht = int(cost * (profit_pct / 100))
                        sell_price = cost + profit_baht
                        
                        q = f"<b>{name}</b> ซื้อของมาในราคา <b>{cost:,} บาท</b> ถ้านำไปขายต่อเพื่อให้ได้กำไร <b>{profit_pct}%</b> <br>เขาจะต้องขายสินค้าชิ้นนี้ไปในราคากี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (คำนวณกำไร):</b><br>
                        <b>ขั้นตอนที่ 1: คำนวณหาจำนวนเงินกำไร</b><br>
                        👉 กำไร {profit_pct}% หมายความว่า ต้องเอาราคาทุนไปคูณ {profit_pct} แล้วหาร 100<br>
                        👉 ตั้งสมการหากำไร: {cost:,} <b style='color:red;'>× {profit_pct} ÷ 100</b><br>
                        👉 คำนวณตัดทอน (ตัดเลข 0 สองตัวทิ้ง): {cost:,} ÷ 100 = {cost//100}<br>
                        👉 นำไปคูณเปอร์เซ็นต์: {cost//100} × {profit_pct} = <b>{profit_baht:,} บาท</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: จำนวนเงินกำไร = {profit_baht:,} บาท</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณหาราคาขายรวม</b><br>
                        👉 สมการ: ราคาขาย = ราคาทุน + กำไรที่อยากได้<br>
                        👉 แทนค่าลงไป: ราคาขาย = {cost:,} <b style='color:green;'>+ {profit_baht:,}</b> = <b>{sell_price:,}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: ราคาขายรวม = {sell_price:,} บาท</b><br>
                        <b>ตอบ: {sell_price:,} บาท</b></span>"""
                        
                elif scenario == "exam":
                    students = random.choice([40, 50, 100, 200, 250, 500])
                    fail_pct = random.choice([5, 10, 15, 20, 25, 30])
                    pass_pct = 100 - fail_pct
                    failed_count = int(students * (fail_pct / 100))
                    passed_count = students - failed_count
                    
                    if is_challenge:
                        q = f"โรงเรียนแห่งหนึ่งมีผู้เข้าสอบทั้งหมด <b>{students:,} คน</b> ปรากฏว่ามีผู้สอบผ่าน <b>{pass_pct}%</b> ของผู้เข้าสอบทั้งหมด<br>จงหาว่ามีผู้ที่ <b>'สอบไม่ผ่าน' (สอบตก)</b> กี่คน?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (พลิกแพลงเปอร์เซ็นต์):</b><br>
                        โจทย์หลอกให้เปอร์เซ็นต์คนสอบผ่าน แต่ดันถามหาคนสอบตก!<br>
                        <b>ขั้นตอนที่ 1: หาเปอร์เซ็นต์ของคนสอบตก</b><br>
                        👉 นักเรียนทั้งหมดคือ 100% หักคนที่สอบผ่าน {pass_pct}%<br>
                        👉 จะได้เปอร์เซ็นต์คนตก = 100 - {pass_pct} = <b>{fail_pct}%</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณหาจำนวนคนจากเปอร์เซ็นต์</b><br>
                        👉 นำเปอร์เซ็นต์คนตกไปคูณจำนวนเด็กทั้งหมด<br>
                        👉 ตั้งสมการ: {students:,} <b style='color:red;'>× {fail_pct} ÷ 100</b><br>
                        👉 ตัด 0 แล้วคำนวณ: {students//100} × {fail_pct} = <b>{failed_count:,} คน</b><br>
                        <b>ตอบ: {failed_count:,} คน</b></span>"""
                    else:
                        q = f"โรงเรียนแห่งหนึ่งมีนักเรียน <b>{students:,} คน</b> สำรวจพบว่ามีนักเรียนสายตาสั้น <b>{fail_pct}%</b> ของนักเรียนทั้งหมด<br>โรงเรียนนี้มีนักเรียนที่สายตาสั้นกี่คน?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: แปลงเปอร์เซ็นต์เป็นสมการ</b><br>
                        👉 {fail_pct}% หมายความว่า ถ้ามีนักเรียน 100 คน จะสายตาสั้น {fail_pct} คน<br>
                        👉 นำไปคูณกับจำนวนนักเรียนทั้งหมด: {students:,} <b style='color:red;'>× {fail_pct} ÷ 100</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณตัดทอนตัวเลข</b><br>
                        👉 นำ {students:,} ÷ 100 = <b>{students//100}</b><br>
                        👉 นำไปคูณเปอร์เซ็นต์: {students//100} × {fail_pct} = <b>{failed_count:,} คน</b><br>
                        <b>ตอบ: {failed_count:,} คน</b></span>"""
                        
                else: # interest
                    principal = random.choice([5000, 10000, 15000, 20000, 50000])
                    interest_rate = random.randint(2, 8)
                    interest_baht = int(principal * (interest_rate / 100))
                    total_money = principal + interest_baht
                    
                    if is_challenge:
                        q = f"<b>{name}</b> นำเงินไปฝากธนาคาร <b>{principal:,} บาท</b> ได้รับอัตราดอกเบี้ย <b>{interest_rate}% ต่อปี</b><br>เมื่อฝากครบ 1 ปี เขาไปถอนเงินออกมาทั้งหมดเพื่อปิดบัญชี เขาจะได้รับเงินรวมทั้งหมดกี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ร้อยละดอกเบี้ยเงินฝาก):</b><br>
                        <b>ขั้นตอนที่ 1: คำนวณหาจำนวนเงินดอกเบี้ยที่ได้รับ</b><br>
                        👉 ดอกเบี้ย {interest_rate}% หมายความว่า ฝาก 100 บาท จะได้เงินเพิ่ม {interest_rate} บาท<br>
                        👉 ตั้งสมการหาดอกเบี้ย: {principal:,} <b style='color:red;'>× {interest_rate} ÷ 100</b><br>
                        👉 คำนวณ: ตัด 0 ทิ้งสองตัว {principal//100} × {interest_rate} = <b>{interest_baht:,} บาท</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณหาเงินรวม (เงินต้น + ดอกเบี้ย)</b><br>
                        👉 เมื่อถอนปิดบัญชี จะได้ทั้งเงินต้นที่ฝากไว้และดอกเบี้ยที่งอกเงย<br>
                        👉 เงินต้น {principal:,} <b style='color:green;'>+ ดอกเบี้ย {interest_baht:,}</b> = <b>{total_money:,} บาท</b><br>
                        <b>ตอบ: {total_money:,} บาท</b></span>"""
                    else:
                        q = f"<b>{name}</b> นำเงินไปฝากธนาคาร <b>{principal:,} บาท</b> ได้รับอัตราดอกเบี้ย <b>{interest_rate}% ต่อปี</b><br>เมื่อฝากครบ 1 ปี เขาจะได้รับ <b>'เฉพาะเงินดอกเบี้ย'</b> กี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: แปลงเปอร์เซ็นต์ดอกเบี้ย</b><br>
                        👉 ดอกเบี้ย {interest_rate}% ของเงินต้น คือการนำเงินต้นไปคูณ {interest_rate} แล้วหารด้วย 100<br>
                        👉 ตั้งสมการ: {principal:,} <b style='color:red;'>× {interest_rate} ÷ 100</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณหาผลลัพธ์</b><br>
                        👉 ตัด 0 ของเงินต้นทิ้ง 2 ตัว จะได้ {principal//100}<br>
                        👉 นำไปคูณเปอร์เซ็นต์: {principal//100} × {interest_rate} = <b>{interest_baht:,} บาท</b><br>
                        <b>ตอบ: ได้ดอกเบี้ย {interest_baht:,} บาท</b></span>"""

            elif actual_sub_t == "สมการและโจทย์ปัญหาสมการ":
                scenario = random.choice(["money", "animal_legs", "age"])
                
                if scenario == "money":
                    if is_challenge:
                        two_names = random.sample(NAMES, 2)
                        n1 = two_names[0]
                        n2 = two_names[1]
                        mult = random.randint(2, 5)
                        sum_val = random.randint(20, 50) * (mult + 1)
                        base_val = sum_val // (mult + 1)
                        large_val = base_val * mult
                        
                        q = f"<b>{n1}</b> และ <b>{n2}</b> มีเงินรวมกันทั้งหมด <b>{sum_val:,} บาท</b> <br>ถ้า <b>{n1}</b> มีเงินเป็น <b>{mult} เท่า</b> ของ <b>{n2}</b> จงหาว่า <b>{n1}</b> มีเงินกี่บาท?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แก้สมการตัวแปรเดียว):</b><br>
                        <b>ขั้นตอนที่ 1: กำหนดตัวแปรแทนสิ่งที่ยังไม่รู้</b><br>
                        👉 ให้เงินของ {n2} เป็น X บาท<br>
                        👉 เนื่องจาก {n1} มีเงินเป็น {mult} เท่าของ {n2} ดังนั้น {n1} มีเงิน = <b>{mult}X บาท</b><br>
                        <b>ขั้นตอนที่ 2: สร้างสมการจากโจทย์</b><br>
                        👉 โจทย์บอกว่า 2 คนนี้มีเงิน "รวมกัน" เท่ากับ {sum_val:,} บาท<br>
                        👉 ตั้งสมการ: (เงินของ {n1}) + (เงินของ {n2}) = {sum_val:,}<br>
                        👉 แทนค่า: <b>{mult}X + X = {sum_val:,}</b><br>
                        👉 นำ X มารวมกัน: มี X อยู่ {mult} ตัว บวกกับ X อีก 1 ตัว กลายเป็น <b>{mult+1}X</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: {mult+1}X = {sum_val:,}</b><br>
                        <b>ขั้นตอนที่ 3: แก้สมการหาค่า X</b><br>
                        👉 กำจัดเลข {mult+1} ที่คูณอยู่ ด้วยการย้ายไปหาร: <br>
                        &nbsp;&nbsp;&nbsp; X = {sum_val:,} <b style='color:red;'>÷ {mult+1}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: X (เงินของ {n2}) = {base_val:,} บาท</b><br>
                        <b>ขั้นตอนที่ 4: หาคำตอบตามที่โจทย์ถาม</b><br>
                        👉 โจทย์ถามหาเงินของ {n1} (ซึ่งก็คือ {mult}X)<br>
                        👉 นำไปคูณ: {mult} × {base_val:,} = <b>{large_val:,} บาท</b><br>
                        <b>ตอบ: {large_val:,} บาท</b></span>"""
                    else:
                        x = random.randint(15, 60)
                        a = random.randint(10, 40)
                        c = x + a
                        q = f"จงแก้สมการหาค่า <b>X</b> จากสมการ: <br><br><span style='font-size:24px; font-weight:bold; margin-left: 20px; color:#2980b9;'>X - {a} = {c-a}</span>"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (คุณสมบัติการเท่ากัน):</b><br>
                        เป้าหมายในการแก้สมการคือ การย้ายข้างตัวเลขเพื่อให้ <b>X</b> เหลืออยู่คนเดียวฝั่งซ้ายของเครื่องหมายเท่ากับ<br>
                        <b>ขั้นตอนที่ 1: สังเกตตัวแปรที่ติดอยู่กับ X</b><br>
                        👉 ฝั่งซ้ายมี <b>-{a}</b> ติดอยู่กับ X เราต้องกำจัดมันทิ้งไปให้กลายเป็น 0<br>
                        <b>ขั้นตอนที่ 2: ใช้คุณสมบัติการเท่ากัน (บวกเข้าทั้งสองข้าง)</b><br>
                        👉 เราจะกำจัด -{a} โดยการนำเลข <b>{a} ไปบวกเพิ่มเข้าทั้งสองข้างของสมการ</b><br>
                        👉 เขียนสมการใหม่ได้ว่า: X - {a} <b style='color:green;'>+ {a}</b> = {c-a} <b style='color:green;'>+ {a}</b><br>
                        <b>ขั้นตอนที่ 3: สรุปผลลัพธ์</b><br>
                        👉 ทางฝั่งซ้าย -{a} บวกกับ +{a} จะหักล้างกันเหลือ 0 ทำให้เหลือแค่ X ตัวเดียว<br>
                        👉 ทางฝั่งขวา นำ {c-a} บวกด้วย {a} จะได้คำตอบคือ <b>{x}</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: X = {x}</b><br>
                        <b>ตอบ: {x}</b></span>"""
                        
                elif scenario == "animal_legs":
                    heads = random.randint(20, 50)
                    chickens = random.randint(10, heads-5)
                    pigs = heads - chickens
                    legs = (chickens * 2) + (pigs * 4)
                    
                    if is_challenge:
                        q = f"ฟาร์มแห่งหนึ่งเลี้ยงไก่และหมูรวมกัน <b>{heads} ตัว</b> ถ้านับขาสัตว์ทั้งหมดรวมกันได้ <b>{legs} ขา</b> <br>จงหาว่าในฟาร์มแห่งนี้มี <b>'ไก่'</b> ทั้งหมดกี่ตัว?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ทริคสมมติฐานสัตว์):</b><br>
                        <b>ขั้นตอนที่ 1: สมมติให้สัตว์ทุกตัวยกขาหน้าขึ้น (มีแค่ 2 ขา)</b><br>
                        👉 ถ้าทั้งฟาร์มมีสัตว์ {heads} ตัว และทุกตัวใช้แค่ 2 ขาเดิน จะมีขารวม = {heads} × 2 = <b>{heads*2} ขา</b><br>
                        <b>ขั้นตอนที่ 2: หาขาที่ขาดหายไปจากความเป็นจริง</b><br>
                        👉 แต่ความจริงฟาร์มนี้มีขาถึง {legs} ขา แสดงว่ามีขาซ่อนอยู่!<br>
                        👉 จำนวนขาที่หายไป = {legs} - {heads*2} = <b>{legs - (heads*2)} ขา</b><br>
                        <b>ขั้นตอนที่ 3: หาจำนวนหมู (สัตว์ 4 ขา)</b><br>
                        👉 ขาที่หายไป คือขาหน้าที่หมูแต่ละตัวยกขึ้น (ตัวละ 2 ขา)<br>
                        👉 ดังนั้น จำนวนหมู = {legs - (heads*2)} ÷ 2 = <b>{pigs} ตัว</b><br>
                        <b>ขั้นตอนที่ 4: หาจำนวนไก่ตามที่โจทย์ถาม</b><br>
                        👉 นำสัตว์ทั้งหมดลบด้วยหมู: {heads} - {pigs} = <b>{chickens} ตัว</b><br>
                        <b>ตอบ: มีไก่ {chickens} ตัว</b></span>"""
                    else:
                        q = f"ฟาร์มแห่งหนึ่งเลี้ยงไก่และหมูรวมกัน <b>{heads} ตัว</b> ถ้านับขาสัตว์ทั้งหมดรวมกันได้ <b>{legs} ขา</b> <br>จงหาว่าในฟาร์มแห่งนี้มี <b>'หมู'</b> ทั้งหมดกี่ตัว?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ทริคสมมติฐานสัตว์):</b><br>
                        <b>ขั้นตอนที่ 1: สมมติให้สัตว์ทุกตัวยกขาหน้าขึ้น (มีแค่ 2 ขา)</b><br>
                        👉 ถ้าทั้งฟาร์มมีสัตว์ {heads} ตัว และทุกตัวใช้แค่ 2 ขาเดิน จะมีขารวม = {heads} × 2 = <b>{heads*2} ขา</b><br>
                        <b>ขั้นตอนที่ 2: หาขาที่ขาดหายไปจากความเป็นจริง</b><br>
                        👉 แต่ความจริงฟาร์มนี้มีขาถึง {legs} ขา แสดงว่ามีขาซ่อนอยู่!<br>
                        👉 จำนวนขาที่หายไป = {legs} - {heads*2} = <b>{legs - (heads*2)} ขา</b><br>
                        <b>ขั้นตอนที่ 3: หาจำนวนหมู (สัตว์ 4 ขา)</b><br>
                        👉 ขาที่หายไป คือขาหน้าที่หมูแต่ละตัวยกขึ้น (ตัวละ 2 ขา)<br>
                        👉 ดังนั้น จำนวนหมู = {legs - (heads*2)} ÷ 2 = <b>{pigs} ตัว</b><br>
                        <b>ตอบ: มีหมู {pigs} ตัว</b></span>"""
                        
                else: # age
                    years_diff = random.randint(20, 35)
                    son_age = random.randint(8, 15)
                    dad_age = son_age + years_diff
                    sum_age = dad_age + son_age
                    
                    if is_challenge:
                        q = f"ปัจจุบัน พ่อและลูกมีอายุรวมกัน <b>{sum_age} ปี</b> <br>ถ้าพ่อมีอายุมากกว่าลูกอยู่ <b>{years_diff} ปี</b> จงหาว่า <b>'ลูก'</b> มีอายุกี่ปี?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แก้ปัญหาผลรวม-ผลต่าง):</b><br>
                        <b>ขั้นตอนที่ 1: หักส่วนที่พ่อแก่กว่า (ส่วนเกิน) ทิ้งไปก่อน</b><br>
                        👉 นำอายุรวม หักส่วนที่พ่ออายุเยอะกว่าลูกออกไป: {sum_age} - {years_diff} = <b>{sum_age - years_diff} ปี</b><br>
                        👉 ตอนนี้อายุที่เหลือ จะเป็นอายุที่เท่ากันเป๊ะระหว่างพ่อกับลูก (ซึ่งก็คืออายุของลูกคูณสอง)<br>
                        <b>ขั้นตอนที่ 2: แบ่งอายุออกเป็น 2 ส่วนเท่าๆ กัน</b><br>
                        👉 นำไปแบ่งครึ่ง เพื่อหาอายุของคนอายุน้อยกว่า (ลูก): <br>
                        👉 ({sum_age - years_diff}) ÷ 2 = <b>{son_age} ปี</b><br>
                        <b>ตอบ: ลูกอายุ {son_age} ปี</b></span>"""
                    else:
                        q = f"ปัจจุบัน พ่อและลูกมีอายุรวมกัน <b>{sum_age} ปี</b> <br>ถ้าพ่อมีอายุมากกว่าลูกอยู่ <b>{years_diff} ปี</b> จงหาว่า <b>'พ่อ'</b> มีอายุกี่ปี?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แก้ปัญหาผลรวม-ผลต่าง):</b><br>
                        <b>ขั้นตอนที่ 1: หักส่วนที่พ่อแก่กว่า (ส่วนเกิน) ทิ้งไปก่อน</b><br>
                        👉 นำอายุรวม หักส่วนที่พ่ออายุเยอะกว่าลูกออกไป: {sum_age} - {years_diff} = <b>{sum_age - years_diff} ปี</b><br>
                        👉 ตอนนี้อายุที่เหลือ จะเป็นอายุที่เท่ากันเป๊ะระหว่างพ่อกับลูก (ซึ่งก็คืออายุของลูกคูณสอง)<br>
                        <b>ขั้นตอนที่ 2: แบ่งอายุออกเป็น 2 ส่วนเท่าๆ กัน (หาอายุลูก)</b><br>
                        👉 นำไปแบ่งครึ่ง เพื่อหาอายุลูก: ({sum_age - years_diff}) ÷ 2 = <b>{son_age} ปี</b><br>
                        <b>ขั้นตอนที่ 3: หาอายุพ่อตามที่โจทย์ถาม</b><br>
                        👉 นำอายุลูก ไปบวกส่วนที่หักทิ้งคืนกลับมาให้พ่อ: {son_age} + {years_diff} = <b>{dad_age} ปี</b><br>
                        <b>ตอบ: พ่ออายุ {dad_age} ปี</b></span>"""

            elif actual_sub_t == "แบบรูปและความสัมพันธ์ (Patterns)":
                scenario = random.choice(["number_seq", "matchstick", "fraction_seq"])
                
                if scenario == "number_seq":
                    if is_challenge:
                        pattern_type = random.choice(["square", "cube", "square_plus_one", "double_square"])
                        target_term = random.randint(10, 20)
                        
                        if pattern_type == "square":
                            seq = []
                            for i in range(1, 6):
                                seq.append(i**2)
                            ans = target_term**2
                            formula_txt = "ตำแหน่งที่ N คูณกับตัวเอง (N × N หรือ N²)"
                            calc_txt = f"{target_term} × {target_term}"
                        elif pattern_type == "cube":
                            seq = []
                            for i in range(1, 6):
                                seq.append(i**3)
                            ans = target_term**3
                            formula_txt = "ตำแหน่งที่ N คูณกัน 3 ครั้ง (N × N × N หรือ N³)"
                            calc_txt = f"{target_term} × {target_term} × {target_term}"
                        elif pattern_type == "square_plus_one":
                            seq = []
                            for i in range(1, 6):
                                seq.append(i**2 + 1)
                            ans = target_term**2 + 1
                            formula_txt = "นำตำแหน่งที่ N ยกกำลังสอง แล้วบวกเพิ่มอีก 1 (N² + 1)"
                            calc_txt = f"({target_term} × {target_term}) + 1"
                        else: 
                            seq = []
                            for i in range(1, 6):
                                seq.append(2 * (i**2))
                            ans = 2 * (target_term**2)
                            formula_txt = "นำตำแหน่งที่ N ยกกำลังสอง แล้วคูณด้วย 2 (2 × N²)"
                            calc_txt = f"2 × ({target_term} × {target_term})"
                        
                        seq_str = ", ".join(map(str, seq))
                        
                        svg_graphic = ""
                        if pattern_type == "square":
                            svg_graphic = f'<div style="text-align:center; margin:10px 0;"><svg height="60" width="300">'
                            for i in range(1, 4):
                                x_offset = (i-1)*80 + 20
                                size = 15
                                for r in range(i):
                                    for c in range(i):
                                        svg_graphic += f'<rect x="{x_offset + c*size}" y="{50 - i*size + r*size}" width="{size-2}" height="{size-2}" fill="#3498db" rx="2"/>'
                                svg_graphic += f'<text x="{x_offset + (i*size)/2}" y="58" font-family="sans-serif" font-size="12" text-anchor="middle">{i**2}</text>'
                            svg_graphic += '</svg></div>'

                        q = f"จงพิจารณาแบบรูปของจำนวนต่อไปนี้: <br>{svg_graphic}<span style='font-size:24px; font-weight:bold; margin-left: 20px;'>{seq_str}, ... </span><br>จงหาว่า <b>จำนวนที่ {target_term}</b> ของแบบรูปนี้คือจำนวนใด?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (อนุกรมประยุกต์):</b><br>
                        <b>ขั้นตอนที่ 1: วิเคราะห์ความสัมพันธ์ของตำแหน่งกับตัวเลข</b><br>
                        👉 จำนวนที่ 1 คือ {seq[0]}<br>
                        👉 จำนวนที่ 2 คือ {seq[1]}<br>
                        👉 จำนวนที่ 3 คือ {seq[2]}<br>
                        👉 จำนวนที่ 4 คือ {seq[3]}<br>
                        <b>ขั้นตอนที่ 2: สรุปกฎของแบบรูป (สูตรสมการ)</b><br>
                        👉 เราจะเห็นได้ว่า ตัวเลขในลำดับนั้น เกิดจาก: <b>{formula_txt}</b><br>
                        <b>ขั้นตอนที่ 3: แทนค่าหาคำตอบที่โจทย์ถาม</b><br>
                        👉 โจทย์ถามหาจำนวนที่ {target_term}<br>
                        👉 แทนค่าลงในสมการ: {calc_txt} = <b>{ans:,}</b><br>
                        <b>ตอบ: {ans:,}</b></span>"""
                    else:
                        start_num = random.randint(2, 50)
                        diff = random.randint(4, 15)
                        is_add = random.choice([True, False])
                        
                        if not is_add:
                            start_num = random.randint(200, 500)
                            
                        target_term = random.randint(15, 40)
                        
                        if is_add:
                            ans = start_num + (target_term - 1) * diff
                            seq = []
                            for i in range(4):
                                seq.append(start_num + i * diff)
                            word_diff = f"เพิ่มขึ้น <b>+{diff}</b>"
                            sign = "+"
                        else:
                            ans = start_num - (target_term - 1) * diff
                            seq = []
                            for i in range(4):
                                seq.append(start_num - i * diff)
                            word_diff = f"ลดลง <b>-{diff}</b>"
                            sign = "-"
                        
                        seq_str = ", ".join(map(str, seq))
                        
                        q = f"จงพิจารณาแบบรูปของจำนวนต่อไปนี้: <br><span style='font-size:24px; font-weight:bold; margin-left: 20px;'>{seq_str}, ... </span><br>จงหาว่า <b>จำนวนที่ {target_term}</b> ของแบบรูปนี้คือจำนวนใด?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (อนุกรมเลขคณิต):</b><br>
                        <b>ขั้นตอนที่ 1: หาความห่างของตัวเลข (ระยะห่าง)</b><br>
                        👉 สังเกตจาก {seq[0]} ไป {seq[1]} {word_diff}<br>
                        👉 จาก {seq[1]} ไป {seq[2]} {word_diff}<br>
                        👉 แบบรูปนี้เป็นการ <b>{word_diff} ทีละเท่าๆ กัน</b><br>
                        <b>ขั้นตอนที่ 2: ตั้งสมการความสัมพันธ์ (สูตรลัด)</b><br>
                        👉 การหาก้าวที่ต้องกระโดดทั้งหมด คือ (ตำแหน่งเป้าหมาย - 1)<br>
                        👉 นำก้าวที่ต้องกระโดด ไปคูณกับระยะห่างแต่ละก้าว แล้วค่อยนำไปกระทำกับตัวตั้งต้น<br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการ: คำตอบ = ตัวตั้งต้น {sign} [ (ตำแหน่งเป้าหมาย - 1) × ระยะห่าง ]</b><br>
                        <b>ขั้นตอนที่ 3: แทนค่าคำนวณ</b><br>
                        👉 แทนค่าลงไป: {start_num} <b style='color:red;'>{sign} [ ({target_term} - 1) × {diff} ]</b><br>
                        👉 คำนวณในวงเล็บ: {target_term - 1} × {diff} = <b>{(target_term - 1) * diff}</b><br>
                        👉 คำนวณขั้นสุดท้าย: {start_num} {sign} {(target_term - 1) * diff} = <b>{ans:,}</b><br>
                        <b>ตอบ: {ans:,}</b></span>"""
                
                elif scenario == "matchstick":
                    # ไม้ขีดไฟเรียงเป็นสามเหลี่ยม (1=3, 2=5, 3=7...)
                    target_term = random.randint(15, 35)
                    ans = 2 * target_term + 1
                    
                    if is_challenge:
                        q = f"ถ้านำไม้ขีดไฟมาวางต่อกันเป็นรูปสามเหลี่ยมเรียงต่อกันไปเรื่อยๆ <br>รูปที่ 1 ใช้ไม้ขีดไฟ 3 ก้าน, รูปที่ 2 ใช้ 5 ก้าน, รูปที่ 3 ใช้ 7 ก้าน... <br>จงหาว่า <b>รูปที่ {target_term}</b> จะต้องใช้ไม้ขีดไฟกี่ก้าน?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (วิเคราะห์รูปทรง):</b><br>
                        <b>ขั้นตอนที่ 1: สังเกตการเพิ่มขึ้นของไม้ขีดไฟ</b><br>
                        👉 รูปที่ 1 ใช้ 3 ก้าน<br>
                        👉 รูปที่ 2 ใช้ 5 ก้าน (เพิ่มมา 2 ก้าน)<br>
                        👉 รูปที่ 3 ใช้ 7 ก้าน (เพิ่มมา 2 ก้าน)<br>
                        👉 สรุปได้ว่า สามเหลี่ยม 1 รูปใหม่ที่งอกออกมา จะใช้ไม้ขีดไฟแชร์ร่วมกับอันเดิม จึงใช้เพิ่มแค่รูปละ 2 ก้าน<br>
                        <b>ขั้นตอนที่ 2: ตั้งสมการความสัมพันธ์</b><br>
                        👉 ทุกรูปต้องเริ่มต้นด้วยไม้ขีดไฟ 1 ก้านเป็นฐานหลัก (แกนยืน) แล้วเพิ่มก้านรูปตัว V (ทีละ 2 ก้าน) ตามลำดับ<br>
                        👉 สมการลัด: <b>จำนวนไม้ขีดไฟ = 1 + (ตำแหน่งของรูป × 2)</b><br>
                        <b>ขั้นตอนที่ 3: แทนค่าคำนวณ</b><br>
                        👉 โจทย์ถามหารูปที่ {target_term}<br>
                        👉 แทนค่า: 1 + ({target_term} × 2) = 1 + {target_term * 2} = <b>{ans} ก้าน</b><br>
                        <b>ตอบ: {ans} ก้าน</b></span>"""
                    else:
                        target_term = random.randint(10, 20)
                        ans = 3 * target_term + 1
                        
                        q = f"ถ้านำไม้ขีดไฟมาวางต่อกันเป็นรูปสี่เหลี่ยมจัตุรัสเรียงต่อกันไปเรื่อยๆ <br>รูปที่ 1 ใช้ไม้ขีดไฟ 4 ก้าน, รูปที่ 2 ใช้ 7 ก้าน, รูปที่ 3 ใช้ 10 ก้าน... <br>จงหาว่า <b>รูปที่ {target_term}</b> จะต้องใช้ไม้ขีดไฟกี่ก้าน?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (วิเคราะห์รูปทรง):</b><br>
                        <b>ขั้นตอนที่ 1: สังเกตการเพิ่มขึ้นของไม้ขีดไฟ</b><br>
                        👉 รูปที่ 1 ใช้ 4 ก้าน<br>
                        👉 รูปที่ 2 ใช้ 7 ก้าน (เพิ่มมา 3 ก้าน)<br>
                        👉 รูปที่ 3 ใช้ 10 ก้าน (เพิ่มมา 3 ก้าน)<br>
                        👉 สรุปได้ว่า สี่เหลี่ยมรูปใหม่ที่งอกออกมา จะแชร์กำแพง 1 ด้านกับอันเดิม จึงใช้เพิ่มแค่รูปละ 3 ก้าน<br>
                        <b>ขั้นตอนที่ 2: ตั้งสมการความสัมพันธ์</b><br>
                        👉 ทุกรูปต้องเริ่มต้นด้วยไม้ขีดไฟ 1 ก้านตั้งต้นเสมอ แล้วเพิ่มรูปตัว C (ทีละ 3 ก้าน) ตามลำดับ<br>
                        👉 สมการลัด: <b>จำนวนไม้ขีดไฟ = 1 + (ตำแหน่งของรูป × 3)</b><br>
                        <b>ขั้นตอนที่ 3: แทนค่าคำนวณ</b><br>
                        👉 โจทย์ถามหารูปที่ {target_term}<br>
                        👉 แทนค่า: 1 + ({target_term} × 3) = 1 + {target_term * 3} = <b>{ans} ก้าน</b><br>
                        <b>ตอบ: {ans} ก้าน</b></span>"""
                        
                else: # fraction_seq
                    target_term = random.randint(12, 25)
                    num_ans = target_term
                    den_ans = target_term + 1
                    
                    f1 = get_vertical_fraction(1, 2)
                    f2 = get_vertical_fraction(2, 3)
                    f3 = get_vertical_fraction(3, 4)
                    f_ans = get_vertical_fraction(num_ans, den_ans)
                    
                    q = f"จงพิจารณาแบบรูปของเศษส่วนต่อไปนี้: <br><span style='font-size:24px; font-weight:bold; margin-left: 20px;'>{f1}, {f2}, {f3}, ... </span><br>จงหาว่า <b>จำนวนที่ {target_term}</b> ของแบบรูปนี้คือเศษส่วนใด?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (แบบรูปเศษส่วน):</b><br>
                    <b>ขั้นตอนที่ 1: แยกวิเคราะห์ตัวเศษ (ด้านบน) และตัวส่วน (ด้านล่าง)</b><br>
                    👉 <b>ตัวเศษ (บน):</b> สังเกตว่าเป็น 1, 2, 3... แสดงว่าตัวเศษมีค่า <b>"เท่ากับ"</b> ตำแหน่งของรูปนั้นพอดี<br>
                    👉 <b>ตัวส่วน (ล่าง):</b> สังเกตว่าเป็น 2, 3, 4... แสดงว่าตัวส่วนมีค่า <b>"มากกว่า"</b> ตำแหน่งของรูปอยู่ 1 แต้มเสมอ<br>
                    <b>ขั้นตอนที่ 2: สรุปสมการความสัมพันธ์</b><br>
                    👉 รูปที่ N จะได้เศษส่วนคือ: <b>N / (N+1)</b><br>
                    <b>ขั้นตอนที่ 3: แทนค่าหาคำตอบ</b><br>
                    👉 โจทย์ถามหารูปที่ {target_term}<br>
                    👉 แทน N = {target_term} จะได้ตัวเศษ = {target_term} และตัวส่วน = {target_term} + 1 = {den_ans}<br>
                    <b>ตอบ: {f_ans}</b></span>"""

            elif actual_sub_t == "สถิติและค่าเฉลี่ย":
                scenario = random.choice(["new_friend", "exam_target"])
                
                if scenario == "new_friend":
                    if is_challenge:
                        count1 = random.randint(3, 6)
                        avg1 = random.randint(20, 50)
                        sum1 = count1 * avg1
                        
                        count2 = count1 + 1
                        avg2 = avg1 + random.randint(2, 5)
                        sum2 = count2 * avg2
                        
                        new_item = sum2 - sum1
                        
                        q = f"กลุ่มของ<b>{name}</b>มีสมาชิก <b>{count1} คน</b> มีน้ำหนักตัว 'เฉลี่ย' อยู่ที่ <b>{avg1} กิโลกรัม</b><br>ต่อมามีเพื่อนเดินมาขอเข้ากลุ่มเพิ่มอีก 1 คน ทำให้น้ำหนักเฉลี่ยของกลุ่มเปลี่ยนไปกลายเป็น <b>{avg2} กิโลกรัม</b><br>จงหาว่าเพื่อนคนที่เดินเข้ามาใหม่ มีน้ำหนักกี่กิโลกรัม?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ย้อนกลับหาผลรวม):</b><br>
                        ในเรื่องค่าเฉลี่ย กฎเหล็กคือเราต้อง <b>"แปลงค่าเฉลี่ยให้กลับเป็นผลรวมทั้งหมด"</b> ออกมาให้ได้ก่อนเสมอ!<br>
                        <b>ขั้นตอนที่ 1: หาผลรวมน้ำหนักของกลุ่มเดิม ({count1} คน)</b><br>
                        👉 สูตร: ผลรวม = ค่าเฉลี่ย × จำนวนคน<br>
                        👉 แทนค่า: {avg1} <b style='color:red;'>× {count1}</b> = <b>{sum1} กิโลกรัม</b> (นี่คือน้ำหนักของ {count1} คนแรกชั่งรวมกันบนตาชั่ง)<br>
                        <b>ขั้นตอนที่ 2: หาผลรวมน้ำหนักของกลุ่มใหม่ ({count2} คน)</b><br>
                        👉 เมื่อมีคนเพิ่มมา 1 คน จำนวนคนจะเปลี่ยนเป็น {count2} คน<br>
                        👉 แทนค่ากลุ่มใหม่: {avg2} <b style='color:red;'>× {count2}</b> = <b>{sum2} กิโลกรัม</b> (นี่คือน้ำหนักรวมแบบใหม่หลังคนใหม่ขึ้นตาชั่ง)<br>
                        <b>ขั้นตอนที่ 3: หาน้ำหนักของคนที่เข้ามาเพิ่ม</b><br>
                        👉 น้ำหนักรวมที่เพิ่มขึ้นมา ก็คือน้ำหนักของคนที่เพิ่งเดินเข้ามานั่นเอง!<br>
                        👉 ตั้งสมการ: น้ำหนักคนใหม่ = ผลรวมใหม่ - ผลรวมเดิม<br>
                        👉 แทนค่า: {sum2} <b style='color:red;'>- {sum1}</b> = <b>{new_item} กิโลกรัม</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: น้ำหนักคนใหม่ = {new_item} กก.</b><br>
                        <b>ตอบ: {new_item} กิโลกรัม</b></span>"""
                    else:
                        num_items = random.randint(4, 6)
                        nums = []
                        for _ in range(num_items):
                            nums.append(random.randint(20, 150))
                            
                        total_sum = sum(nums)
                        if total_sum % num_items != 0:
                            nums[-1] += num_items - (total_sum % num_items)
                            total_sum = sum(nums)
                            
                        avg = total_sum // num_items
                        
                        nums_str = ", ".join(map(str, nums[:-1])) + f", และ {nums[-1]}"
                        
                        q = f"<b>{name}</b> ทำการจดบันทึกราคาสินค้า {num_items} ชิ้น ได้แก่ <b>{nums_str} บาท</b><br>จงหาราคา <b>'เฉลี่ย'</b> ของสินค้ากลุ่มนี้?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: เข้าใจสูตรของค่าเฉลี่ย</b><br>
                        👉 สูตรการหาค่าเฉลี่ย = <b>(ผลรวมของข้อมูลทั้งหมด) ÷ (จำนวนข้อมูลที่มี)</b><br>
                        <b>ขั้นตอนที่ 2: หาผลรวมของข้อมูลทั้งหมด</b><br>
                        👉 นำราคาสินค้าทั้ง {num_items} ชิ้นมาบวกเข้าด้วยกัน: <br>
                        &nbsp;&nbsp;&nbsp; {' + '.join(map(str, nums))} = <b>{total_sum:,} บาท</b><br>
                        <b>ขั้นตอนที่ 3: นำไปหารด้วยจำนวนข้อมูล</b><br>
                        👉 เนื่องจากมีสินค้าทั้งหมด {num_items} ชิ้น ให้นำผลรวมไปตั้งหารด้วย {num_items}<br>
                        👉 ตั้งสมการ: {total_sum:,} <b style='color:red;'>÷ {num_items}</b> = <b>{avg:,} บาท</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: ราคาเฉลี่ย = {avg:,} บาท</b><br>
                        <b>ตอบ: {avg:,} บาท</b></span>"""
                        
                else: # exam_target
                    exams = random.randint(3, 4)
                    target_avg = random.randint(80, 95)
                    total_needed = (exams + 1) * target_avg
                    
                    current_scores = []
                    for _ in range(exams):
                        current_scores.append(random.randint(target_avg-10, target_avg+5))
                        
                    current_sum = sum(current_scores)
                    needed = total_needed - current_sum
                    
                    while needed > 100 or needed < 0:
                        target_avg = random.randint(80, 90)
                        total_needed = (exams + 1) * target_avg
                        current_scores = []
                        for _ in range(exams):
                            current_scores.append(random.randint(target_avg-5, target_avg+5))
                        current_sum = sum(current_scores)
                        needed = total_needed - current_sum
                    
                    scores_str = ", ".join(map(str, current_scores))
                    
                    if is_challenge:
                        q = f"<b>{name}</b> สอบไปแล้ว <b>{exams} วิชา</b> ได้คะแนนดังนี้: <b>{scores_str} คะแนน</b><br>เขาเหลือสอบอีก 1 วิชาสุดท้าย หากเขาต้องการให้คะแนน <b>'เฉลี่ย'</b> ของทุกวิชารวมกันเป็น <b>{target_avg} คะแนน</b> พอดี<br>จงหาว่าวิชาสุดท้ายเขาต้องสอบให้ได้กี่คะแนน?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (เป้าหมายค่าเฉลี่ย):</b><br>
                        การจะควบคุมค่าเฉลี่ยได้ เราต้องคำนวณ <b>"คะแนนรวมเป้าหมาย"</b> ออกมาให้ได้ก่อน<br>
                        <b>ขั้นตอนที่ 1: หาคะแนนรวมเป้าหมายทั้งหมด ({exams+1} วิชา)</b><br>
                        👉 เขาต้องการค่าเฉลี่ย = {target_avg} คะแนน จากจำนวนทั้งหมด {exams+1} วิชา<br>
                        👉 ตั้งสมการ: {target_avg} × {exams+1} = <b>{total_needed} คะแนน</b> (นี่คือเป้าหมายที่ต้องทำให้ถึง)<br>
                        <b>ขั้นตอนที่ 2: หาคะแนนรวมที่มีอยู่ในมือตอนนี้ ({exams} วิชา)</b><br>
                        👉 นำคะแนนที่สอบผ่านไปแล้วมาบวกกัน: {' + '.join(map(str, current_scores))} = <b>{current_sum} คะแนน</b><br>
                        <b>ขั้นตอนที่ 3: หาคะแนนวิชาสุดท้ายที่ต้องทำเพิ่ม</b><br>
                        👉 นำเป้าหมาย ลบด้วย สิ่งที่มีอยู่: {total_needed} - {current_sum} = <b>{needed} คะแนน</b><br>
                        <b>ตอบ: ต้องสอบให้ได้ {needed} คะแนน</b></span>"""
                    else:
                        q = f"<b>{name}</b> สอบไปแล้ว <b>{exams} วิชา</b> ได้คะแนนดังนี้: <b>{scores_str} คะแนน</b><br>จงหาคะแนน <b>'เฉลี่ย'</b> ของการสอบ {exams} วิชานี้?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: เข้าใจสูตรของค่าเฉลี่ย</b><br>
                        👉 สูตรการหาค่าเฉลี่ย = <b>(ผลรวมคะแนนทั้งหมด) ÷ (จำนวนวิชาที่มี)</b><br>
                        <b>ขั้นตอนที่ 2: หาผลรวมของคะแนนทั้งหมด</b><br>
                        👉 นำคะแนนทั้ง {exams} วิชามาบวกเข้าด้วยกัน: <br>
                        &nbsp;&nbsp;&nbsp; {' + '.join(map(str, current_scores))} = <b>{current_sum} คะแนน</b><br>
                        <b>ขั้นตอนที่ 3: นำไปหารด้วยจำนวนวิชา</b><br>
                        👉 ให้นำผลรวมไปตั้งหารด้วย {exams}<br>
                        👉 ตั้งสมการ: {current_sum} <b style='color:red;'>÷ {exams}</b> = <b>{current_sum/exams:.2f} คะแนน</b><br>
                        <b>ตอบ: {current_sum/exams:.2f} คะแนน</b></span>"""

            elif actual_sub_t == "ปริมาตรและความจุ":
                scenario = random.choice(["fish_tank", "pour_water"])
                
                if scenario == "fish_tank":
                    if is_challenge:
                        w = random.randint(5, 10)
                        l = random.randint(10, 20)
                        h = random.randint(5, 15)
                        vol = w * l * h
                        water_h = random.randint(2, h-2)
                        water_vol = w * l * water_h
                        fill_vol = vol - water_vol
                        
                        q = f"ตู้ปลาทรงสี่เหลี่ยมมุมฉาก กว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b> <br>ตอนนี้มีน้ำบรรจุอยู่ในตู้ โดยวัดระดับความสูงของน้ำได้ <b>{water_h} ซม.</b><br>จะต้องเติมน้ำลงไปอีกกี่ <b>ลูกบาศก์เซนติเมตร</b> น้ำจึงจะเต็มตู้ปลาพอดี?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ปริมาตรทรงสี่เหลี่ยมมุมฉาก):</b><br>
                        สูตรการหาปริมาตร = <b>กว้าง × ยาว × สูง</b><br>
                        <b>ขั้นตอนที่ 1: หาความสูงของน้ำที่ต้องเติมเพิ่ม</b><br>
                        👉 ตู้สูงทั้งหมด {h} ซม. ตอนนี้มีน้ำอยู่แล้ว {water_h} ซม.<br>
                        👉 ตั้งสมการหาช่องว่างด้านบนที่เหลือ: ความสูงส่วนที่ยังว่าง = {h} - {water_h} = <b>{h - water_h} ซม.</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณปริมาตรน้ำที่ต้องเติมลงไปในช่องว่าง</b><br>
                        👉 เราจะคำนวณปริมาตรเฉพาะส่วนที่ยังว่างอยู่ (ฐานกว้างและยาวจะเท่าตู้ปลาเดิม เปลี่ยนแค่ความสูง)<br>
                        👉 แทนค่าในสูตร: กว้าง({w}) <b style='color:red;'>×</b> ยาว({l}) <b style='color:red;'>×</b> สูงของส่วนที่ว่าง({h - water_h})<br>
                        👉 คำนวณทีละขั้น: ฐานของตู้คือ {w} × {l} = <b>{w * l} ตร.ซม.</b><br>
                        👉 จากนั้นนำไปคูณความสูง: {w * l} × {h - water_h} = <b>{fill_vol:,} ลบ.ซม.</b><br>
                        &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: ปริมาตรน้ำที่ต้องเติมเพิ่ม = {fill_vol:,} ลบ.ซม.</b><br>
                        <b>ตอบ: {fill_vol:,} ลูกบาศก์เซนติเมตร</b></span>"""
                    else:
                        w = random.randint(10, 20)
                        l = random.randint(20, 40)
                        h = random.randint(10, 30)
                        vol = w * l * h
                        
                        q = f"กล่องพลาสติกทรงสี่เหลี่ยมมุมฉาก มีความกว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b> <br>กล่องใบนี้มีความจุทั้งหมดกี่ <b>ลูกบาศก์เซนติเมตร</b>?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                        <b>ขั้นตอนที่ 1: ใช้สูตรการหาปริมาตร</b><br>
                        👉 สูตร: ปริมาตร = <b>กว้าง × ยาว × สูง</b><br>
                        <b>ขั้นตอนที่ 2: แทนค่าลงในสูตร</b><br>
                        👉 แทนค่า: {w} × {l} × {h}<br>
                        👉 คำนวณคู่แรก: {w} × {l} = <b>{w * l}</b><br>
                        👉 นำไปคูณความสูงต่อ: {w * l} × {h} = <b>{vol:,} ลบ.ซม.</b><br>
                        <b>ตอบ: {vol:,} ลูกบาศก์เซนติเมตร</b></span>"""
                        
                else: # pour_water
                    jug = random.choice([250, 500, 750])
                    tank_l = random.randint(5, 15)
                    tank_ml = tank_l * 1000
                    ans = tank_ml // jug
                    
                    if is_challenge:
                        q = f"ถังน้ำใบหนึ่งมีความจุ <b>{tank_l} ลิตร</b> ถ้านำเหยือกที่มีความจุ <b>{jug} มิลลิลิตร</b> <br>ตักน้ำใส่ถังใบนี้ที่กำลังว่างเปล่าจนกว่าจะเต็มถังพอดี จะต้องตักน้ำทั้งหมดกี่ครั้ง?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (การแปลงหน่วยความจุ):</b><br>
                        เราไม่สามารถนำ ลิตร มาหารด้วย มิลลิลิตร ได้โดยตรง ต้องแปลงหน่วยให้เท่ากันก่อนเสมอ!<br>
                        <b>ขั้นตอนที่ 1: แปลงความจุของถัง (ลิตร ➔ มิลลิลิตร)</b><br>
                        👉 เรารู้ว่า 1 ลิตร = 1,000 มิลลิลิตร<br>
                        👉 นำความจุของถังไปคูณ: {tank_l} × 1,000 = <b>{tank_ml:,} มิลลิลิตร</b><br>
                        <b>ขั้นตอนที่ 2: คำนวณหาจำนวนครั้งที่ต้องตัก</b><br>
                        👉 ให้นำปริมาตรรวมของถัง ตั้งหารด้วยปริมาตรของเหยือก 1 ใบ<br>
                        👉 ตั้งสมการ: {tank_ml:,} <b style='color:red;'>÷ {jug}</b> = <b>{ans} ครั้ง</b><br>
                        <b>ตอบ: {ans} ครั้ง</b></span>"""
                    else:
                        multiplier = 1000
                        u_major = "ลิตร"
                        u_minor = "มิลลิลิตร"
                        op_choices = ["+", "-"]
                        op = random.choice(op_choices)
                        v1_maj = random.randint(3, 10)
                        v1_min = random.randint(100, 900)
                        
                        if op == "-":
                            v2_maj = random.randint(1, v1_maj-1)
                        else:
                            v2_maj = random.randint(1, 10)
                            
                        v2_min = random.randint(100, 900)
                        
                        if op == "-":
                            if v1_min >= v2_min:
                                v1_min, v2_min = v2_min, v1_min + 50
                                if v2_min >= 1000: 
                                    v2_min = 950
                        
                        svg = draw_beakers_svg(v1_maj, v1_min, v2_maj, v2_min)
                        
                        if op == "+":
                            q = f"{svg}จากรูป ถ้านำน้ำจากทั้งสองถังมา<b>รวมกัน</b> จะได้ปริมาตรน้ำทั้งหมดเท่าไร?"
                        else:
                            q = f"{svg}จากรูป ถัง A มีปริมาตรน้ำ<b>ต่างกับ</b>ถัง B อยู่เท่าไร?"
                            
                        table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                        
                        if op == "+":
                            word_op = "บวก"
                        else:
                            word_op = "ลบ"
                            
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{word_op}ข้ามหน่วย):</b><br>
                        👉 หลักการสำคัญคือ ต้องตั้งหน่วย "ลิตร" และ "มิลลิลิตร" ให้ตรงกัน<br>
                        👉 ถ้ายอดรวมหน่วยมิลลิลิตรเกิน 1,000 ให้ปัดทดเป็น 1 ลิตร<br>
                        👉 ถ้ายอดลบหน่วยมิลลิลิตรไม่พอ ให้ขอยืมหน่วยลิตรมา 1 ลิตร (ซึ่งเท่ากับ 1,000 มิลลิลิตร)<br>
                        {table_html}
                        <b>ตอบ: {ans_str}</b></span>"""

            elif actual_sub_t == "การแปลงหน่วยและเปรียบเทียบ":
                scenario = random.choice(["compare_dec", "time_convert"])
                
                if scenario == "time_convert":
                    days = random.randint(2, 5)
                    hours = random.randint(5, 20)
                    total_h = days * 24 + hours
                    
                    diff_h = random.choice([-10, -5, 5, 10])
                    compare_h = total_h + diff_h
                    
                    if is_challenge:
                        q = f"การเดินทางรอบที่ 1 ใช้เวลา <b>{days} วัน {hours} ชั่วโมง</b> <br>การเดินทางรอบที่ 2 ใช้เวลา <b>{compare_h} ชั่วโมง</b><br>จงเปรียบเทียบว่าการเดินทางรอบใดใช้เวลา <b>นานกว่ากัน</b> และนานกว่ากันกี่ชั่วโมง?"
                        
                        if total_h > compare_h:
                            ans_txt = f"รอบที่ 1 นานกว่าอยู่ {total_h - compare_h} ชั่วโมง"
                        elif compare_h > total_h:
                            ans_txt = f"รอบที่ 2 นานกว่าอยู่ {compare_h - total_h} ชั่วโมง"
                        else:
                            ans_txt = "ทั้งสองรอบใช้เวลาเท่ากัน"
                            
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (การแปลงหน่วยเวลา):</b><br>
                        <b>ขั้นที่ 1: แปลงหน่วยของรอบที่ 1 ให้เป็น 'ชั่วโมง' ล้วนๆ</b><br>
                        👉 เรารู้ว่า 1 วัน = 24 ชั่วโมง<br>
                        👉 ดังนั้น {days} วัน = {days} × 24 = <b>{days * 24} ชั่วโมง</b><br>
                        👉 นำไปรวมกับเศษชั่วโมงเดิม: {days * 24} + {hours} = <b>{total_h} ชั่วโมง</b><br>
                        <b>ขั้นที่ 2: เปรียบเทียบตัวเลข</b><br>
                        👉 รอบที่ 1: {total_h} ชั่วโมง<br>
                        👉 รอบที่ 2: {compare_h} ชั่วโมง<br>
                        👉 นำมาลบกันหาผลต่าง: | {total_h} - {compare_h} | = <b>{abs(total_h - compare_h)} ชั่วโมง</b><br>
                        <b>ตอบ: {ans_txt}</b></span>"""
                    else:
                        q = f"การเดินทางไปดาวอังคารใช้เวลา <b>{days} วัน {hours} ชั่วโมง</b> <br>คิดเป็นเวลาการเดินทางทั้งหมดกี่ชั่วโมง?"
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (การแปลงหน่วยเวลา):</b><br>
                        <b>ขั้นที่ 1: แปลงหน่วยของวันให้เป็น 'ชั่วโมง'</b><br>
                        👉 1 วัน = 24 ชั่วโมง<br>
                        👉 นำจำนวนวันไปคูณ: {days} × 24 = <b>{days * 24} ชั่วโมง</b><br>
                        <b>ขั้นที่ 2: นำไปบวกเศษชั่วโมงที่เหลือ</b><br>
                        👉 {days * 24} + {hours} = <b>{total_h} ชั่วโมง</b><br>
                        <b>ตอบ: {total_h} ชั่วโมง</b></span>"""
                else: # compare_dec
                    type_choices = ["m_cm", "km_m", "kg_g"]
                    selected_type = random.choice(type_choices)
                    
                    if selected_type == "m_cm":
                        multiplier = 100
                        u_major = "เมตร"
                        u_minor = "เซนติเมตร"
                    elif selected_type == "km_m":
                        multiplier = 1000
                        u_major = "กิโลเมตร"
                        u_minor = "เมตร"
                    else:
                        multiplier = 1000
                        u_major = "กิโลกรัม"
                        u_minor = "กรัม"
                        
                    dec_choices = [0.1, 0.25, 0.5, 0.75, 0.2, 0.8]
                    dec_val = random.choice(dec_choices)
                    val_major_int = random.randint(2, 15)
                    val_A_major = val_major_int + dec_val
                    val_A_minor_total = int(val_A_major * multiplier)
                    
                    diff_amount = random.randint(10, 200)
                    if random.choice([True, False]):
                        val_B_minor_total = val_A_minor_total + diff_amount
                    else:
                        val_B_minor_total = val_A_minor_total - diff_amount
                        
                    if random.choice([True, False]):
                        item_A = f"{val_A_major} {u_major}"
                        item_B = f"{val_B_minor_total:,} {u_minor}"
                        val_A = val_A_minor_total
                        val_B = val_B_minor_total
                        is_a_major = True
                    else:
                        item_A = f"{val_B_minor_total:,} {u_minor}"
                        item_B = f"{val_A_major} {u_major}"
                        val_A = val_B_minor_total
                        val_B = val_A_minor_total
                        is_a_major = False
                        
                    if val_A > val_B:
                        if selected_type == "kg_g":
                            comp_word = "หนักกว่า"
                        elif selected_type == "m_cm":
                            comp_word = "ยาวกว่า"
                        else:
                            comp_word = "ไกลกว่า"
                    else:
                        if selected_type == "kg_g":
                            comp_word = "เบากว่า"
                        elif selected_type == "m_cm":
                            comp_word = "สั้นกว่า"
                        else:
                            comp_word = "ใกล้กว่า"
                    
                    q = f"จงเปรียบเทียบว่า <b>{item_A}</b> กับ <b>{item_B}</b> สิ่งใดมีค่ามากกว่ากัน?<br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (เปรียบเทียบทศนิยมกับจำนวนเต็ม):</b><br>
                    <b>ขั้นที่ 1: ทบทวนความสัมพันธ์ของหน่วย</b><br>
                    👉 1 {u_major} เท่ากับ <b>{multiplier:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: แปลงหน่วยให้เหมือนกัน (แปลง {u_major} เป็น {u_minor})</b><br>"""
                    
                    if is_a_major:
                        sol += f"👉 ฝั่งซ้าย: {val_A_major} {u_major} = {val_A_major} × {multiplier:,} = <b>{val_A_minor_total:,} {u_minor}</b><br>"
                        sol += f"👉 ฝั่งขวา: มีหน่วยเป็น {u_minor} อยู่แล้ว คือ <b>{val_B_minor_total:,} {u_minor}</b><br>"
                    else:
                        sol += f"👉 ฝั่งซ้าย: มีหน่วยเป็น {u_minor} อยู่แล้ว คือ <b>{val_B_minor_total:,} {u_minor}</b><br>"
                        sol += f"👉 ฝั่งขวา: {val_A_major} {u_major} = {val_A_major} × {multiplier:,} = <b>{val_A_minor_total:,} {u_minor}</b><br>"
                    
                    sol += f"<b>ขั้นที่ 3: เปรียบเทียบตัวเลข</b><br>"
                    
                    if val_A > val_B:
                        sign = ">"
                        word_ans = "ฝั่งซ้าย มากกว่า"
                    else:
                        sign = "<"
                        word_ans = "ฝั่งขวา มากกว่า"
                        
                    sol += f"👉 จะเห็นว่า <b>{val_A:,} {sign} {val_B:,}</b><br>"
                    sol += f"<b>ตอบ: {word_ans}</b></span>"

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
    try: 
        return html_str.split('<body>')[1].split('</body>')[0]
    except IndexError: 
        return html_str

def create_page(level, sub_t, questions, is_key=False, q_margin="20px", ws_height="180px", brand_name="", is_challenge=False):
    if is_challenge:
        title_suffix = " 🔥 [CHALLENGE MODE]"
    else:
        title_suffix = ""
        
    if is_key:
        title = f"เฉลย (Answer Key){title_suffix}"
    else:
        title = f"ข้อสอบ (O-NET P.6){title_suffix}"
    
    if not is_key:
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
        """
    else:
        student_info = ""
        
    if is_challenge:
        header_color = "#e67e22"
    else:
        header_color = "#2980b9"
        
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Sarabun', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }}
        .header h2 {{ color: {header_color}; }}
        .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.8; }}
        .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }}
        .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }}
        .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f4f6f7; border-left: 4px solid {header_color}; border-radius: 4px; line-height: 1.8; }}
        .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
    </style></head><body>
    <div class="header"><h2>{title}</h2><p><b>หมวดหมู่:</b> {sub_t} ({level})</p></div>
    {student_info}"""
    
    for i, item in enumerate(questions, 1):
        html += f'<div class="q-box"><b>ข้อที่ {i}.</b> '
        if is_key:
            html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
        else:
            html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับแสดงวิธีคิดวิเคราะห์เชิงสมการ...</div><div class="ans-line">ตอบ: </div>'
        html += '</div>'
        
    if brand_name: 
        html += f'<div class="page-footer">&copy; 2026 {brand_name} | สงวนลิขสิทธิ์</div>'
        
    html += "</body></html>"
    return html

# ==========================================
# 4. Streamlit UI (Sidebar & Result Grouping)
# ==========================================
st.sidebar.markdown("## ⚙️ พารามิเตอร์การสร้างข้อสอบ")

selected_level = st.sidebar.selectbox("🎯 เลือกระดับชั้น:", ["ประถมศึกษาปีที่ 6 (O-NET)"])
selected_sub = st.sidebar.selectbox("📝 เลือกแนวข้อสอบ (พร้อมเฉลยละเอียด):", onet_p6_topics + ["🌟 สุ่มรวมทุกแนว (ป.6 O-NET)"])

num_input = st.sidebar.number_input("🔢 จำนวนข้อ:", min_value=1, max_value=100, value=10)

st.sidebar.markdown("---")
is_challenge = st.sidebar.toggle("🔥 โหมด Challenge (ระดับยากพิเศษสำหรับเด็กเก่ง)", value=False)

if is_challenge:
    st.markdown("""
    <script>
        const header = window.parent.document.querySelector('.main-header');
        if(header) { header.classList.add('challenge'); header.querySelector('span').innerText = '🔥 Challenge Mode'; header.querySelector('span').style.background = '#e74c3c'; header.querySelector('span').style.color = '#fff'; }
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

spacing_options = ["แคบ", "ปานกลาง", "กว้าง", "กว้างพิเศษ"]
spacing_level = st.sidebar.select_slider(
    "↕️ ความสูงของพื้นที่ทดเลข:", 
    options=spacing_options, 
    value="กว้าง"
)

if spacing_level == "แคบ": 
    q_margin = "15px"
    ws_height = "100px"
elif spacing_level == "ปานกลาง": 
    q_margin = "20px"
    ws_height = "180px"
elif spacing_level == "กว้าง": 
    q_margin = "30px"
    ws_height = "280px"
else: 
    q_margin = "40px"
    ws_height = "400px"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 ตั้งค่าแบรนด์")
brand_name = st.sidebar.text_input("🏷️ ชื่อแบรนด์ / ผู้สอน:", value="บ้านทีเด็ด")

if is_challenge:
    btn_text = "🚀 สั่งสร้างข้อสอบระดับ Challenge!"
else:
    btn_text = "🚀 สั่งสร้างข้อสอบ O-NET เดี๋ยวนี้"

if st.sidebar.button(btn_text, type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบข้อสอบ O-NET พร้อมจัดทำเฉลยแบบ Step-by-Step ทุกบรรทัด..."):
        
        qs = generate_questions_logic(selected_level, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_level, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name, is_challenge=is_challenge)
        html_k = create_page(selected_level, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name, is_challenge=is_challenge)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        if is_challenge:
            bg_color = "#2c3e50"
        else:
            bg_color = "#525659"
            
        if is_challenge:
            header_color = "#e67e22"
        else:
            header_color = "#2980b9"
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: {bg_color}; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .header h2 {{ color: {header_color}; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.8; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f4f6f7; border-left: 4px solid {header_color}; border-radius: 4px; line-height: 1.8; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}</style></head><body>{ebook_body}</body></html>"""

        if is_challenge:
            mode_name = "Challenge"
        else:
            mode_name = "Normal"
            
        safe_sub = selected_sub.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename_base = f"ONET_P6_{mode_name}_{safe_sub}_{int(time.time())}"
        
        st.session_state['ebook_html'] = full_ebook_html
        st.session_state['filename_base'] = filename_base
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}_Full_EBook.html", full_ebook_html.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_Worksheet.html", html_w.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_AnswerKey.html", html_k.encode('utf-8'))
        st.session_state['zip_data'] = zip_buffer.getvalue()

if 'ebook_html' in st.session_state:
    st.success(f"✅ โค้ดฉบับเต็มสมบูรณ์ 100% ไม่มีตัดไม่มีบรรทัดยุบรวม! พร้อมรูปแบบโจทย์ที่หลากหลายยิ่งขึ้นครับ")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
