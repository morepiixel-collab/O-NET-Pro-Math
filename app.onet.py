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

def draw_distance_route_svg(p_names, p_emojis, dist_texts):
    width = 500
    height = 120
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    svg += f'<line x1="50" y1="60" x2="250" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
    
    if len(p_names) == 3: 
        svg += f'<line x1="250" y1="60" x2="450" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
        
    svg += f'<text x="150" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[0]}</text>'
    
    if len(p_names) == 3: 
        svg += f'<text x="350" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[1]}</text>'
        
    xs = [50, 250, 450]
    for i, name in enumerate(p_names):
        emoji = p_emojis[i]
        svg += f'<circle cx="{xs[i]}" cy="60" r="28" fill="#ecf0f1" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<text x="{xs[i]}" y="68" font-size="28" text-anchor="middle">{emoji}</text>'
        svg += f'<text x="{xs[i]}" y="110" font-family="Sarabun" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{name}</text>'
        
    svg += '</svg></div>'
    return svg

def get_prefix(grade):
    if grade in ["ป.1", "ป.2", "ป.3"]: 
        return "<b style='color: #2c3e50; margin-right: 5px;'>ประโยคสัญลักษณ์:</b>"
    return ""

def generate_decimal_vertical_html(a, b, op, is_key=False):
    str_a = f"{a:.2f}"
    str_b = f"{b:.2f}"
    
    if op == '+':
        ans = a + b
    else:
        ans = round(a - b, 2)
        
    str_ans = f"{ans:.2f}"
    max_len = max(len(str_a), len(str_b), len(str_ans)) + 1 
    
    str_a = str_a.rjust(max_len, " ")
    str_b = str_b.rjust(max_len, " ")
    str_ans = str_ans.rjust(max_len, " ")
    
    strike = [False] * max_len
    top_marks = [""] * max_len
    
    if is_key:
        if op == '+':
            carry = 0
            for i in range(max_len - 1, -1, -1):
                if str_a[i] == '.': 
                    continue
                    
                if str_a[i].strip():
                    da = int(str_a[i])
                else:
                    da = 0
                    
                if str_b[i].strip():
                    db = int(str_b[i])
                else:
                    db = 0
                    
                s = da + db + carry
                carry = s // 10
                
                if carry > 0 and i > 0:
                    next_i = i - 1
                    if str_a[next_i] == '.': 
                        next_i -= 1
                    if next_i >= 0: 
                        top_marks[next_i] = str(carry)
        elif op == '-':
            a_chars = list(str_a)
            b_chars = list(str_b)
            
            a_digits = []
            for c in a_chars:
                if c.strip() and c != '.':
                    a_digits.append(int(c))
                else:
                    a_digits.append(0)
                    
            b_digits = []
            for c in b_chars:
                if c.strip() and c != '.':
                    b_digits.append(int(c))
                else:
                    b_digits.append(0)
                    
            for i in range(max_len - 1, -1, -1):
                if str_a[i] == '.': 
                    continue
                if a_digits[i] < b_digits[i]:
                    for j in range(i-1, -1, -1):
                        if str_a[j] == '.': 
                            continue
                        if a_digits[j] > 0 and str_a[j].strip() != "":
                            strike[j] = True
                            a_digits[j] -= 1
                            top_marks[j] = str(a_digits[j])
                            for k in range(j+1, i):
                                if str_a[k] == '.': 
                                    continue
                                strike[k] = True
                                a_digits[k] = 9
                                top_marks[k] = "9"
                            strike[i] = True
                            a_digits[i] += 10
                            top_marks[i] = str(a_digits[i])
                            break
                            
    a_tds = ""
    for i in range(max_len):
        if str_a[i].strip():
            val = str_a[i].strip()
        else:
            val = ""
            
        if str_a[i] == '.': 
            val = "."
            
        td_content = val
        if val and val != '.':
            mark = top_marks[i]
            if strike[i] and is_key: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{val}</span></div>'
            elif mark and is_key: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{val}</span></div>'
        a_tds += f"<td style='width: 35px; text-align: center; height: 50px; vertical-align: bottom;'>{td_content}</td>"
        
    b_tds = ""
    for c in str_b:
        if c.strip():
            display_c = c.strip()
        elif c == '.':
            display_c = '.'
        else:
            display_c = ''
        b_tds += f"<td style='width: 35px; text-align: center; border-bottom: 2px solid #000; height: 40px; vertical-align: bottom;'>{display_c}</td>"
    
    ans_tds = ""
    if is_key: 
        for c in str_ans:
            if c.strip():
                display_c = c.strip()
            elif c == '.':
                display_c = '.'
            else:
                display_c = ''
            ans_tds += f"<td style='width: 35px; text-align: center; color: red; font-weight: bold; height: 45px; vertical-align: bottom;'>{display_c}</td>"
    else: 
        for _ in str_ans:
            ans_tds += f"<td style='width: 35px; height: 45px;'></td>"
        
    html_out = f"""<div style="display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;">
        <div style="display: inline-block; font-family: 'Sarabun', sans-serif; font-size: 32px; line-height: 1.2;">
            <table style="border-collapse: collapse;">
                <tr>
                    <td style="width: 20px;"></td>
                    {a_tds}
                    <td style="width: 50px; text-align: left; padding-left: 15px; vertical-align: middle;" rowspan="2">{op}</td>
                </tr>
                <tr>
                    <td></td>
                    {b_tds}
                </tr>
                <tr>
                    <td></td>
                    {ans_tds}
                    <td></td>
                </tr>
                <tr>
                    <td></td>
                    <td colspan="{max_len}" style="border-bottom: 6px double #000; height: 10px;"></td>
                    <td></td>
                </tr>
            </table>
        </div>
    </div>"""
    return html_out

def generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False):
    div_str = str(dividend)
    div_len = len(div_str)
    
    if not is_key:
        ans_tds_list = []
        for _ in div_str:
            ans_tds_list.append('<td style="width: 35px; height: 45px;"></td>')
        ans_tds_list.append('<td style="width: 35px;"></td>')
        
        div_tds_list = []
        for i, c in enumerate(div_str):
            if i == 0:
                left_border = "border-left: 3px solid #000;"
            else:
                left_border = ""
            div_tds_list.append(f'<td style="width: 35px; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px; height: 50px; vertical-align: bottom;">{c}</td>')
        div_tds_list.append('<td style="width: 35px;"></td>')
        
        empty_rows = ""
        for _ in range(div_len + 1): 
            empty_rows += f"<tr><td style='border: none;'></td>"
            for _ in range(div_len + 1):
                empty_rows += f"<td style='width: 35px; height: 45px;'></td>"
            empty_rows += "</tr>"
            
        return f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>{empty_rows}</table></div></div>"
    
    steps = []
    current_val_str = ""
    ans_str = ""
    has_started = False
    
    for i, digit in enumerate(div_str):
        current_val_str += digit
        current_val = int(current_val_str)
        q = current_val // divisor
        mul_res = q * divisor
        rem = current_val - mul_res
        
        if not has_started and q == 0 and i < len(div_str) - 1:
             if rem != 0:
                 current_val_str = str(rem)
             else:
                 current_val_str = ""
             continue
             
        has_started = True
        ans_str += str(q)
        
        cur_chars = list(str(current_val))
        m_chars = list(str(mul_res).zfill(len(str(current_val))))
        
        c_dig = []
        for c in cur_chars:
            c_dig.append(int(c))
            
        m_dig = []
        for c in m_chars:
            m_dig.append(int(c))
        
        top_m = [""] * len(c_dig)
        strik = [False] * len(c_dig)
        
        for idx_b in range(len(c_dig) - 1, -1, -1):
            if c_dig[idx_b] < m_dig[idx_b]:
                for j in range(idx_b-1, -1, -1):
                    if c_dig[j] > 0:
                        strik[j] = True
                        c_dig[j] -= 1
                        top_m[j] = str(c_dig[j])
                        for k in range(j+1, idx_b): 
                            strik[k] = True
                            c_dig[k] = 9
                            top_m[k] = "9"
                        strik[idx_b] = True
                        c_dig[idx_b] += 10
                        top_m[idx_b] = str(c_dig[idx_b])
                        break
                        
        steps.append({'mul_res': mul_res, 'rem': rem, 'col_index': i, 'top_m': top_m, 'strik': strik})
        
        if rem != 0:
            current_val_str = str(rem)
        else:
            current_val_str = ""
        
    ans_padded = ans_str.rjust(div_len, " ")
    ans_tds_list = []
    for c in ans_padded:
        ans_tds_list.append(f'<td style="width: 35px; text-align: center; color: red; font-weight: bold; font-size: 38px;">{c.strip()}</td>')
    ans_tds_list.append('<td style="width: 35px;"></td>') 
    
    div_tds_list = []
    if len(steps) > 0:
        s0 = steps[0]
    else:
        s0 = None
        
    if s0:
        s0_start = s0['col_index'] + 1 - len(s0['top_m'])
    else:
        s0_start = 0
        
    for i, c in enumerate(div_str):
        if i == 0:
            left_border = "border-left: 3px solid #000;"
        else:
            left_border = ""
            
        td_content = c
        if is_key and s0 and s0_start <= i <= s0['col_index']:
            t_idx = i - s0_start
            mark = s0['top_m'][t_idx]
            is_strik = s0['strik'][t_idx]
            if is_strik: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{c}</span></div>'
            elif mark: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{c}</span></div>'
        div_tds_list.append(f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px;">{td_content}</td>')
    div_tds_list.append('<td style="width: 35px;"></td>') 
    
    html = f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>"
    
    for idx, step in enumerate(steps):
        mul_res_str = str(step['mul_res'])
        pad_len = step['col_index'] + 1 - len(mul_res_str)
        mul_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len and i <= step['col_index']:
                digit_idx = i - pad_len
                if i <= step['col_index']:
                    border_b = "border-bottom: 2px solid #000;"
                else:
                    border_b = ""
                mul_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b}">{mul_res_str[digit_idx]}</td>'
            elif i == step['col_index'] + 1: 
                mul_tds += '<td style="width: 35px; text-align: center; font-size: 38px; color: #333; position: relative; top: -24px;">-</td>'
            else: 
                mul_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{mul_tds}</tr>"
        
        if idx == len(steps) - 1:
            is_last_step = True
        else:
            is_last_step = False
            
        if not is_last_step:
            next_step = steps[idx+1]
        else:
            next_step = None
            
        if next_step:
            ns_start = next_step['col_index'] + 1 - len(next_step['top_m'])
        else:
            ns_start = 0
            
        rem_str = str(step['rem'])
        if not is_last_step:
            next_digit = div_str[step['col_index'] + 1]
        else:
            next_digit = ""
            
        if rem_str != "0" or is_last_step:
            display_str = rem_str
        else:
            display_str = ""
        
        if not is_last_step and display_str == "": 
            pass
        else: 
            display_str += next_digit
            
        if display_str == "": 
            display_str = next_digit
        
        if not is_last_step:
            pad_len_rem = step['col_index'] + 1 - len(display_str) + 1
        else:
            pad_len_rem = step['col_index'] + 1 - len(display_str) + 0
            
        rem_tds = ""
        for i in range(div_len + 1):
            if not is_last_step:
                upper_bound = step['col_index'] + 1
            else:
                upper_bound = step['col_index'] + 0
                
            if i >= pad_len_rem and i <= upper_bound:
                digit_idx = i - pad_len_rem
                char_val = display_str[digit_idx]
                td_content = char_val
                if is_key and next_step and ns_start <= i <= next_step['col_index']:
                    t_idx = i - ns_start
                    mark = next_step['top_m'][t_idx]
                    is_strik = next_step['strik'][t_idx]
                    if is_strik: 
                        td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{char_val}</span></div>'
                    elif mark: 
                        td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{char_val}</span></div>'
                
                if is_last_step:
                    border_b2 = "border-bottom: 6px double #000;"
                else:
                    border_b2 = ""
                    
                rem_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b2}">{td_content}</td>'
            else: 
                rem_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{rem_tds}</tr>"
        
    html += "</table></div></div>"
    html += f"<div style='margin-top: 15px; color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>1) นำตัวหาร ({divisor}) ไปหารตัวตั้ง ({dividend}) ทีละหลักจากซ้ายไปขวา<br>2) ท่องสูตรคูณแม่ {divisor} ว่าคูณอะไรแล้วได้ใกล้เคียงหรือเท่ากับตัวตั้งในหลักนั้นที่สุด (แต่ห้ามเกิน)<br>3) ใส่ผลลัพธ์ไว้ด้านบน และนำผลคูณมาลบกันด้านล่าง<br>4) ดึงตัวเลขในหลักถัดไปลงมา แล้วทำซ้ำขั้นตอนเดิมจนหมดทุกหลัก</div>"
    return html

def generate_thai_number_text(num_str):
    thai_nums = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    parts = str(num_str).replace(",", "").split(".")
    int_part = parts[0]
    
    if len(parts) > 1:
        dec_part = parts[1]
    else:
        dec_part = ""
    
    def read_int(s):
        if s == "0" or s == "": 
            return "ศูนย์"
        res = ""
        length = len(s)
        for i, digit in enumerate(s):
            d = int(digit)
            if d == 0: 
                continue
            pos = length - i - 1
            if pos == 1 and d == 2: 
                res += "ยี่สิบ"
            elif pos == 1 and d == 1: 
                res += "สิบ"
            elif pos == 0 and d == 1 and length > 1: 
                res += "เอ็ด"
            else: 
                res += thai_nums[d] + positions[pos]
        return res
        
    int_text = read_int(int_part)
    
    if dec_part:
        dec_text = "จุด"
        for d in dec_part:
            dec_text += thai_nums[int(d)]
    else:
        dec_text = ""
        
    return int_text + dec_text

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

            elif actual_sub_t == "โจทย์ปัญหา ค.ร.น. (เวลา/จุดนัดพบ)":
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

            elif actual_sub_t == "โจทย์ปัญหาเศษส่วนประยุกต์":
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
                    den_choices = [4, 5, 6, 8, 10]
                    den = random.choice(den_choices)
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

            elif actual_sub_t == "ร้อยละ เปอร์เซ็นต์ (กำไร/ลดราคา)":
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

            elif actual_sub_t == "สมการและโจทย์ปัญหาสมการ":
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

            elif actual_sub_t == "แบบรูปและความสัมพันธ์ (Patterns)":
                if is_challenge:
                    target_term = random.randint(10, 20)
                    ans = target_term ** 2
                    q = f"จงพิจารณาแบบรูปของจำนวนต่อไปนี้: <br><span style='font-size:24px; font-weight:bold; margin-left: 20px;'>1, 4, 9, 16, 25, ... </span><br>จงหาว่า <b>จำนวนที่ {target_term}</b> ของแบบรูปนี้คือจำนวนใด?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (อนุกรมยกกำลังสอง):</b><br>
                    <b>ขั้นตอนที่ 1: วิเคราะห์ความสัมพันธ์ของตำแหน่งกับตัวเลข</b><br>
                    👉 จำนวนที่ 1 คือ 1 ซึ่งเกิดจาก (1 × 1) หรือ 1²<br>
                    👉 จำนวนที่ 2 คือ 4 ซึ่งเกิดจาก (2 × 2) หรือ 2²<br>
                    👉 จำนวนที่ 3 คือ 9 ซึ่งเกิดจาก (3 × 3) หรือ 3²<br>
                    👉 จำนวนที่ 4 คือ 16 ซึ่งเกิดจาก (4 × 4) หรือ 4²<br>
                    <b>ขั้นตอนที่ 2: สรุปกฎของแบบรูป (สูตรสมการ)</b><br>
                    👉 เราจะเห็นได้ชัดเจนว่า "ตัวเลขในลำดับนั้น เกิดจาก ตำแหน่งที่ตั้ง นำมาคูณด้วยตัวมันเอง (ยกกำลังสอง)"<br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: จำนวนที่ N = N × N</b><br>
                    <b>ขั้นตอนที่ 3: แทนค่าหาคำตอบที่โจทย์ถาม</b><br>
                    👉 โจทย์ถามหาจำนวนที่ {target_term}<br>
                    👉 แทน N ด้วย {target_term} ลงในสมการ: {target_term} × {target_term} = <b>{ans:,}</b><br>
                    <b>ตอบ: {ans:,}</b></span>"""
                else:
                    start_num = random.randint(2, 15)
                    diff = random.randint(3, 9)
                    target_term = random.randint(15, 30)
                    ans = start_num + (target_term - 1) * diff
                    
                    seq = []
                    for i in range(4):
                        seq.append(start_num + i * diff)
                    
                    q = f"จงพิจารณาแบบรูปของจำนวนต่อไปนี้: <br><span style='font-size:24px; font-weight:bold; margin-left: 20px;'>{seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ... </span><br>จงหาว่า <b>จำนวนที่ {target_term}</b> ของแบบรูปนี้คือจำนวนใด?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (อนุกรมเลขคณิต):</b><br>
                    <b>ขั้นตอนที่ 1: หาความห่างของตัวเลข (ระยะห่าง)</b><br>
                    👉 สังเกตจาก {seq[0]} ไป {seq[1]} เพิ่มขึ้น <b>+{diff}</b><br>
                    👉 จาก {seq[1]} ไป {seq[2]} เพิ่มขึ้น <b>+{diff}</b><br>
                    👉 แบบรูปนี้เป็นการ <b>เพิ่มขึ้นทีละ {diff} เท่าๆ กัน</b><br>
                    <b>ขั้นตอนที่ 2: ตั้งสมการความสัมพันธ์ (สูตรลัด)</b><br>
                    👉 การหาก้าวที่ต้องกระโดดทั้งหมด คือ (ตำแหน่งเป้าหมาย - 1)<br>
                    👉 นำก้าวที่ต้องกระโดด ไปคูณกับระยะห่างแต่ละก้าว แล้วค่อยไปบวกตัวตั้งต้น<br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการ: คำตอบ = ตัวตั้งต้น + [ (ตำแหน่งเป้าหมาย - 1) × ระยะห่าง ]</b><br>
                    <b>ขั้นตอนที่ 3: แทนค่าคำนวณ</b><br>
                    👉 แทนค่าลงไป: {start_num} <b style='color:green;'>+ [ ({target_term} - 1) × {diff} ]</b><br>
                    👉 คำนวณในวงเล็บ: {target_term - 1} × {diff} = <b>{(target_term - 1) * diff}</b><br>
                    👉 นำไปบวกตัวเริ่มต้น: {start_num} + {(target_term - 1) * diff} = <b>{ans:,}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: จำนวนที่ {target_term} = {ans:,}</b><br>
                    <b>ตอบ: {ans:,}</b></span>"""

            elif actual_sub_t == "สถิติและค่าเฉลี่ย":
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
                    nums = []
                    for _ in range(4):
                        nums.append(random.randint(10, 50))
                        
                    total_sum = sum(nums)
                    avg = total_sum // 4
                    if total_sum % 4 != 0:
                        nums[3] += 4 - (total_sum % 4)
                        total_sum = sum(nums)
                        avg = total_sum // 4
                        
                    q = f"<b>{name}</b> ทำการจดบันทึกราคาสินค้า 4 ชิ้น ได้แก่ <b>{nums[0]}, {nums[1]}, {nums[2]}, และ {nums[3]} บาท</b><br>จงหาราคา <b>'เฉลี่ย'</b> ของสินค้ากลุ่มนี้?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: เข้าใจสูตรของค่าเฉลี่ย</b><br>
                    👉 สูตรการหาค่าเฉลี่ย = <b>(ผลรวมของข้อมูลทั้งหมด) ÷ (จำนวนข้อมูลที่มี)</b><br>
                    <b>ขั้นตอนที่ 2: หาผลรวมของข้อมูลทั้งหมด</b><br>
                    👉 นำราคาสินค้าทั้ง 4 ชิ้นมาบวกเข้าด้วยกัน: <br>
                    &nbsp;&nbsp;&nbsp; {nums[0]} + {nums[1]} + {nums[2]} + {nums[3]} = <b>{total_sum} บาท</b><br>
                    <b>ขั้นตอนที่ 3: นำไปหารด้วยจำนวนข้อมูล</b><br>
                    👉 เนื่องจากมีสินค้าทั้งหมด 4 ชิ้น ให้นำผลรวมไปตั้งหารด้วย 4<br>
                    👉 ตั้งสมการ: {total_sum} <b style='color:red;'>÷ 4</b> = <b>{avg} บาท</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด: ราคาเฉลี่ย = {avg} บาท</b><br>
                    <b>ตอบ: {avg} บาท</b></span>"""

            elif actual_sub_t == "ปริมาตรและความจุ":
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
                cat_choices = ["compare", "add_sub"]
                q_cat = random.choice(cat_choices)
                
                type_choices = ["m_cm", "km_m", "kg_g", "ton_kg"]
                selected_type = random.choice(type_choices)
                
                if selected_type == "m_cm":
                    u_major = "เมตร"
                    u_minor = "เซนติเมตร"
                    multiplier = 100
                elif selected_type == "km_m":
                    u_major = "กิโลเมตร"
                    u_minor = "เมตร"
                    multiplier = 1000
                elif selected_type == "kg_g":
                    u_major = "กิโลกรัม"
                    u_minor = "กรัม"
                    multiplier = 1000
                else: 
                    u_major = "ตัน"
                    u_minor = "กิโลกรัม"
                    multiplier = 1000
                    
                if q_cat == "compare":
                    if is_challenge:
                        val_major = random.randint(5, 50)
                    else:
                        val_major = random.randint(2, 20)
                        
                    val_minor = random.randint(50, multiplier-10)
                    
                    total_minor_1 = (val_major * multiplier) + val_minor
                    
                    case_choices = ["greater", "less", "equal"]
                    case = random.choice(case_choices)
                    
                    if case == "equal":
                        total_minor_2 = total_minor_1
                    elif case == "greater":
                        total_minor_2 = total_minor_1 - random.randint(1, multiplier - 1)
                    else:
                        total_minor_2 = total_minor_1 + random.randint(1, multiplier - 1)

                    str_val_1 = f"{val_major} {u_major} {val_minor} {u_minor}"
                    str_val_2 = f"{total_minor_2:,} {u_minor}"

                    if random.choice([True, False]):
                        item_A = str_val_1
                        item_B = str_val_2
                        val_A = total_minor_1
                        val_B = total_minor_2
                    else:
                        item_A = str_val_2
                        item_B = str_val_1
                        val_A = total_minor_2
                        val_B = total_minor_1

                    if total_minor_1 == total_minor_2:
                        final_ans = "เท่ากัน"
                    else:
                        if selected_type in ["m_cm", "km_m"]:
                            if val_A > val_B:
                                final_ans = "ยาวกว่า/ไกลกว่า"
                            else:
                                final_ans = "สั้นกว่า/ใกล้กว่า"
                        else:
                            if val_A > val_B:
                                final_ans = "หนักกว่า"
                            else:
                                final_ans = "เบากว่า"
                        
                    q = f"จงเปรียบเทียบว่า <b>{item_A}</b> กับ <b>{item_B}</b> สิ่งใดมีค่า <b>มากกว่า/ยาวกว่า/หนักกว่า</b> กัน?<br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นที่ 1: ทบทวนความสัมพันธ์ของหน่วย</b><br>
                    👉 เรารู้ว่า 1 {u_major} มีค่าเท่ากับ <b>{multiplier:,} {u_minor}</b> เสมอ<br>
                    <b>ขั้นที่ 2: สร้างสมการแปลงหน่วยให้เป็นหน่วยย่อยเหมือนกันทั้งหมด</b><br>
                    👉 เราจะแปลงฝั่ง <b>{str_val_1}</b> ให้เป็นหน่วย <b>{u_minor}</b> เพียวๆ เพื่อให้ง่ายต่อการเปรียบเทียบ<br>
                    👉 นำไปเข้าสมการ: นำ {val_major} ไปคูณ {multiplier:,} แล้วบวกด้วย {val_minor} <br>
                    👉 ({val_major} <b style='color:red;'>× {multiplier:,}</b>) <b style='color:green;'>+ {val_minor}</b> = {val_major * multiplier:,} <b style='color:green;'>+ {val_minor}</b><br>
                    &nbsp;&nbsp;&nbsp; <b>👉 สมการล่าสุด:</b> แปลงได้เป็น <b>{total_minor_1:,} {u_minor}</b><br>
                    <b>ขั้นที่ 3: เปรียบเทียบตัวเลข</b><br>"""

                    if val_A == val_B:
                        sol += f"👉 จะเห็นว่า {total_minor_1:,} {u_minor} มีค่า <b>เท่ากับ</b> {total_minor_2:,} {u_minor} พอดี!<br>"
                    else:
                        if val_A < val_B:
                            comp_sign = "น้อยกว่า"
                        else:
                            comp_sign = "มากกว่า"
                            
                        sol += f"👉 นำมาเปรียบเทียบฝั่งซ้าย ({val_A:,} {u_minor}) กับฝั่งขวา ({val_B:,} {u_minor})<br>"
                        sol += f"👉 จะเห็นว่าตัวเลข {val_A:,} <b>{comp_sign}</b> {val_B:,}<br>"

                    sol += f"<b>ตอบ: ฝั่งซ้าย {final_ans} ฝั่งขวา</b></span>"
                else: 
                    op_choices = ["+", "-"]
                    op = random.choice(op_choices)
                    v1_maj = random.randint(3, 20)
                    v1_min = random.randint(1, multiplier-1)
                    
                    if op == "-":
                        v2_maj = random.randint(1, v1_maj-1)
                    else:
                        v2_maj = random.randint(1, 20)
                        
                    v2_min = random.randint(1, multiplier-1)
                    
                    if op == "-":
                        if v1_min >= v2_min:
                            v1_min, v2_min = v2_min, v1_min + (multiplier//2)
                            if v2_min >= multiplier: 
                                v2_min = multiplier - 1
                    
                    if op == "+":
                        q = f"จงหาผลลัพธ์ของ: <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> <b>รวมกับ</b> <b>{v2_maj} {u_major} {v2_min} {u_minor}</b>"
                    else:
                        q = f"จงหาผลลัพธ์ของ: <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> <b>ต่างกับ</b> <b>{v2_maj} {u_major} {v2_min} {u_minor} อยู่เท่าไร?</b>"
                        
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    
                    if op == "+":
                        word_op = "บวก"
                    else:
                        word_op = "ลบ"
                        
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{word_op}แบบข้ามหน่วย):</b><br>
                    👉 หลักการสำคัญคือ ต้องตั้งหน่วย <b>{u_major}</b> และ <b>{u_minor}</b> ให้ตรงกัน<br>
                    👉 ถ้ายอดรวมหน่วย{u_minor}ถึง {multiplier:,} เมื่อไหร่ ให้ปัดทดไปเป็น 1 {u_major}<br>
                    👉 ถ้ายอดลบหน่วย{u_minor}ไม่พอ ให้ขอยืมหน่วย{u_major}มา 1 (ซึ่งจะแตกออกเท่ากับ {multiplier:,} {u_minor})<br>
                    {table_html}
                    <b>ตอบ: {ans_str}</b></span>"""

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
    st.success(f"✅ สำเร็จแล้วครับ! แยกหัวข้อ ห.ร.ม. และ ค.ร.น. ออกจากกัน พร้อมแสดงตารางหารสั้นในเฉลยเรียบร้อยแล้วครับ")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
