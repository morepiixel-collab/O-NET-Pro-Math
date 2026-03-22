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
                    
                    new_nums = []
                    for n in current_nums:
                        new_nums.append(n // i)
                    current_nums = new_nums
                    
                    found_factor = True
                    break
            else: # ค.ร.น.
                divisible_count = 0
                for n in current_nums:
                    if n % i == 0:
                        divisible_count += 1
                        
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
            nums_str = ", ".join(map(str, nums))
            return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ไม่มีจำนวนเฉพาะใดที่หาร {nums_str} ลงตัวพร้อมกัน<br><b>ดังนั้น ห.ร.ม. = 1</b></span>"
        else:
            ans = math.prod(nums)
            nums_str = " × ".join(map(str, nums))
            return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ไม่มีจำนวนเฉพาะใดที่หารเลขกลุ่มนี้ลงตัวตั้งแต่ 2 จำนวนขึ้นไป<br><b>ขั้นที่ 2:</b> ให้นำตัวเลขทั้งหมดมาคูณกันได้เลย<br><b>ดังนั้น ค.ร.น. = {nums_str} = {ans:,}</b></span>"

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
        
        factors_and_rem = []
        for f in factors:
            factors_and_rem.append(f)
        for n in current_nums:
            if n != 1:
                factors_and_rem.append(n)
                
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

def draw_matchstick_pattern(shape):
    svg = '<div style="text-align:center; margin:15px 0;"><svg height="100" width="550">'
    
    def m_line(x1, y1, x2, y2):
        html_line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#d35400" stroke-width="4" stroke-linecap="round"/>'
        html_line += f'<circle cx="{x1}" cy="{y1}" r="2" fill="#c0392b"/>'
        html_line += f'<circle cx="{x2}" cy="{y2}" r="2" fill="#c0392b"/>'
        return html_line
        
    if shape == "triangle":
        svg += m_line(30, 60, 50, 20)
        svg += m_line(50, 20, 70, 60)
        svg += m_line(30, 60, 70, 60)
        svg += '<text x="50" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 1</text>'
        
        ox = 100
        svg += m_line(ox+30, 60, ox+50, 20)
        svg += m_line(ox+50, 20, ox+70, 60)
        svg += m_line(ox+30, 60, ox+70, 60)
        svg += m_line(ox+70, 60, ox+90, 20)
        svg += m_line(ox+50, 20, ox+90, 20)
        svg += f'<text x="{ox+60}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 2</text>'
        
        ox = 220
        svg += m_line(ox+30, 60, ox+50, 20)
        svg += m_line(ox+50, 20, ox+70, 60)
        svg += m_line(ox+30, 60, ox+70, 60)
        svg += m_line(ox+70, 60, ox+90, 20)
        svg += m_line(ox+50, 20, ox+90, 20)
        svg += m_line(ox+90, 20, ox+110, 60)
        svg += m_line(ox+70, 60, ox+110, 60)
        svg += f'<text x="{ox+70}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 3</text>'
        svg += '<text x="380" y="55" font-size="24" font-weight="bold">. . .</text>'
        
    elif shape == "square":
        svg += m_line(30, 20, 60, 20)
        svg += m_line(60, 20, 60, 50)
        svg += m_line(60, 50, 30, 50)
        svg += m_line(30, 50, 30, 20)
        svg += '<text x="45" y="80" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 1</text>'
        
        ox = 100
        svg += m_line(ox+30, 20, ox+60, 20)
        svg += m_line(ox+60, 20, ox+60, 50)
        svg += m_line(ox+60, 50, ox+30, 50)
        svg += m_line(ox+30, 50, ox+30, 20)
        svg += m_line(ox+60, 20, ox+90, 20)
        svg += m_line(ox+90, 20, ox+90, 50)
        svg += m_line(ox+90, 50, ox+60, 50)
        svg += f'<text x="{ox+60}" y="80" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 2</text>'
        
        ox = 220
        svg += m_line(ox+30, 20, ox+60, 20)
        svg += m_line(ox+60, 20, ox+60, 50)
        svg += m_line(ox+60, 50, ox+30, 50)
        svg += m_line(ox+30, 50, ox+30, 20)
        svg += m_line(ox+60, 20, ox+90, 20)
        svg += m_line(ox+90, 20, ox+90, 50)
        svg += m_line(ox+90, 50, ox+60, 50)
        svg += m_line(ox+90, 20, ox+120, 20)
        svg += m_line(ox+120, 20, ox+120, 50)
        svg += m_line(ox+120, 50, ox+90, 50)
        svg += f'<text x="{ox+75}" y="80" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 3</text>'
        svg += '<text x="390" y="55" font-size="24" font-weight="bold">. . .</text>'
        
    elif shape == "pentagon":
        svg += m_line(30, 60, 60, 60)
        svg += m_line(30, 60, 30, 35)
        svg += m_line(60, 60, 60, 35)
        svg += m_line(30, 35, 45, 15)
        svg += m_line(45, 15, 60, 35)
        svg += '<text x="45" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 1</text>'
        
        ox = 90
        svg += m_line(ox+30, 60, ox+60, 60)
        svg += m_line(ox+30, 60, ox+30, 35)
        svg += m_line(ox+60, 60, ox+60, 35)
        svg += m_line(ox+30, 35, ox+45, 15)
        svg += m_line(ox+45, 15, ox+60, 35)
        svg += m_line(ox+60, 60, ox+90, 60)
        svg += m_line(ox+90, 60, ox+90, 35)
        svg += m_line(ox+60, 35, ox+75, 15)
        svg += m_line(ox+75, 15, ox+90, 35)
        svg += f'<text x="{ox+60}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 2</text>'
        
        ox = 210
        svg += m_line(ox+30, 60, ox+60, 60)
        svg += m_line(ox+30, 60, ox+30, 35)
        svg += m_line(ox+60, 60, ox+60, 35)
        svg += m_line(ox+30, 35, ox+45, 15)
        svg += m_line(ox+45, 15, ox+60, 35)
        svg += m_line(ox+60, 60, ox+90, 60)
        svg += m_line(ox+90, 60, ox+90, 35)
        svg += m_line(ox+60, 35, ox+75, 15)
        svg += m_line(ox+75, 15, ox+90, 35)
        svg += m_line(ox+90, 60, ox+120, 60)
        svg += m_line(ox+120, 60, ox+120, 35)
        svg += m_line(ox+90, 35, ox+105, 15)
        svg += m_line(ox+105, 15, ox+120, 35)
        svg += f'<text x="{ox+75}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 3</text>'
        svg += '<text x="380" y="55" font-size="24" font-weight="bold">. . .</text>'
        
    elif shape == "hexagon":
        def draw_hex(start_x):
            h_svg = ""
            h_svg += m_line(start_x+20, 15, start_x+40, 25)
            h_svg += m_line(start_x+40, 25, start_x+40, 55)
            h_svg += m_line(start_x+40, 55, start_x+20, 65)
            h_svg += m_line(start_x+20, 65, start_x, 55)
            h_svg += m_line(start_x, 55, start_x, 25)
            h_svg += m_line(start_x, 25, start_x+20, 15)
            return h_svg
            
        svg += draw_hex(30)
        svg += '<text x="50" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 1</text>'
        
        ox = 110
        svg += draw_hex(ox+30)
        svg += draw_hex(ox+70)
        svg += f'<text x="{ox+70}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 2</text>'
        
        ox = 250
        svg += draw_hex(ox+30)
        svg += draw_hex(ox+70)
        svg += draw_hex(ox+110)
        svg += f'<text x="{ox+90}" y="85" font-family="Sarabun" font-size="14" fill="#333" text-anchor="middle">รูปที่ 3</text>'
        svg += '<text x="470" y="55" font-size="24" font-weight="bold">. . .</text>'
        
    svg += '</svg></div>'
    return svg

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
                scenario = random.choice(["fruit", "wire", "student"])
                
                if scenario == "fruit":
                    fruit_samples = random.sample(FRUITS, 2)
                    f1 = fruit_samples[0]
                    f2 = fruit_samples[1]
                    
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
                    
                    q = f"ช่างก่อสร้างมีลวดอยู่ 3 เส้น ยาว <b>{l1} ซม., {l2} ซม., และ {l3} ซม.</b> ตามลำดับ <br>ต้องการตัดลวดให้เป็นท่อนสั้นๆ ยาวเท่าๆ กัน โดยให้ได้ <b>'ความยาวมากที่สุด'</b> และไม่ให้เหลือเศษ <br>ลวดที่ถูกตัดแต่ละท่อนจะมีความยาวเท่าไร และจะได้ลวดทั้งหมดกี่ท่อน?"
                    
                    div_table = generate_short_division_html([l1, l2, l3], mode="ห.ร.ม.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ห.ร.ม.):</b><br>
                    โจทย์การตัดแบ่งสิ่งของให้ยาวที่สุดและเท่าๆ กัน คือการหา <b>ห.ร.ม. (หารร่วมมาก)</b><br>
                    <b>ขั้นตอนที่ 1: หาความยาวของลวดต่อท่อน (หา ห.ร.ม.)</b><br>
                    👉 นำความยาวของลวดทั้งสามเส้นมาตั้งหารสั้น<br>
                    {div_table}
                    👉 ตัวเลข ห.ร.ม. ที่ได้คือ <b>{gcd_val}</b> (แสดงว่าลวดแต่ละท่อนจะยาว {gcd_val} ซม.)<br>
                    <b>ขั้นตอนที่ 2: หาจำนวนท่อนทั้งหมด</b><br>
                    👉 นำผลลัพธ์เศษด้านล่างสุดของการหารสั้นมาบวกกันได้เลย<br>
                    👉 {m1} + {m2} + {m3} = <b>{total_pieces} ท่อน</b><br>
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
                    👉 ดูจากตัวเลขด้านล่างสุดของตารางหารสั้น นำจำนวนกลุ่มมาบวกกัน: {m1} + {m2} = <b>{total_groups} กลุ่ม</b><br>
                    <b>ตอบ: จัดได้กลุ่มละ {gcd_val} คน และได้ทั้งหมด {total_groups} กลุ่ม</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหา ค.ร.น. (เวลา/จุดนัดพบ)":
                scenario = random.choice(["clock", "bus", "run"])
                
                if scenario == "clock":
                    items_list = ["นาฬิกาปลุก", "ระฆัง", "สัญญาณไฟ"]
                    item_word = random.choice(items_list)
                    time_choices = [8, 10, 12, 15, 20, 24, 30]
                    
                    if is_challenge:
                        time_samples = random.sample(time_choices, 4)
                        l1 = time_samples[0]
                        l2 = time_samples[1]
                        l3 = time_samples[2]
                        l4 = time_samples[3]
                        
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
                        {div_table}
                        👉 จะได้รอบเวลาที่ลงตัวพร้อมกันคือ <b>{lcm} วินาที</b><br>
                        <b>ขั้นตอนที่ 2: แปลงหน่วยวินาทีเป็นนาทีและวินาที</b><br>
                        👉 1 นาที มี 60 วินาที ให้นำ {lcm} ÷ 60<br>
                        👉 จะได้ผลลัพธ์เท่ากับ <b>{text_ans}</b> พอดี<br>
                        <b>ตอบ: {text_ans}</b></span>"""
                    else:
                        time_samples = random.sample(time_choices, 3)
                        l1 = time_samples[0]
                        l2 = time_samples[1]
                        l3 = time_samples[2]
                        
                        lcm = lcm_multiple(l1, l2, l3)
                        
                        q = f"{item_word} 3 ชิ้น ทำงานด้วยจังหวะที่ต่างกัน ชิ้นแรกดังทุกๆ {l1} นาที, ชิ้นที่สอง {l2} นาที และชิ้นที่สาม {l3} นาที <br>ถ้าเพิ่งดังพร้อมกันไป อีกกี่นาทีข้างหน้าจึงจะดังพร้อมกันอีกครั้ง?"
                        
                        div_table = generate_short_division_html([l1, l2, l3], mode="ค.ร.น.")
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                        โจทย์ที่ถามหาจุดที่ "เกิดขึ้นพร้อมกันอีกครั้ง" คือการหา <b>ค.ร.น. (คูณร่วมน้อย)</b><br>
                        <b>ขั้นตอนที่ 1: ตั้งหารสั้นหา ค.ร.น.</b><br>
                        {div_table}
                        <b>ขั้นตอนที่ 2: สรุปผล ค.ร.น.</b><br>
                        👉 เมื่อนำตัวเลขด้านหน้าและเศษด้านล่างมาคูณกันทั้งหมด จะได้ผลลัพธ์เท่ากับ <b>{lcm}</b><br>
                        👉 แสดงว่าอีก {lcm} นาที วงจรรอบเวลาของทั้ง 3 ชิ้นจะวนมาตรงกันพอดีเป๊ะ<br>
                        <b>ตอบ: อีก {lcm} นาที</b></span>"""
                
                elif scenario == "bus":
                    start_h = random.randint(6, 10)
                    time_choices = [15, 20, 25, 30, 40, 45, 60]
                    time_samples = random.sample(time_choices, 3)
                    t1 = time_samples[0]
                    t2 = time_samples[1]
                    t3 = time_samples[2]
                    
                    lcm = lcm_multiple(t1, t2, t3)
                    
                    add_h = lcm // 60
                    add_m = lcm % 60
                    ans_h = start_h + add_h
                    ans_m = add_m
                    
                    q = f"สถานีขนส่งแห่งหนึ่ง ปล่อยรถโดยสาร 3 สาย <br>สาย A ออกทุกๆ <b>{t1} นาที</b>, สาย B ออกทุกๆ <b>{t2} นาที</b>, และสาย C ออกทุกๆ <b>{t3} นาที</b><br>ถ้ารถทั้ง 3 สายเพิ่งออกเดินทางพร้อมกันตอนเวลา <b>0{start_h}:00 น.</b> รถทั้ง 3 สายจะออกเดินทางพร้อมกันอีกครั้งเวลาใด?"
                    
                    div_table = generate_short_division_html([t1, t2, t3], mode="ค.ร.น.")
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                    <b>ขั้นตอนที่ 1: หาเวลาร่วมที่รถจะออกพร้อมกัน (หา ค.ร.น.)</b><br>
                    {div_table}
                    👉 ค.ร.น. คือ <b>{lcm} นาที</b> แสดงว่าต้องรออีก {lcm} นาที รถถึงจะออกพร้อมกัน<br>
                    <b>ขั้นตอนที่ 2: แปลงหน่วยเป็นชั่วโมงและนาที</b><br>
                    👉 นำ {lcm} นาที ÷ 60 จะได้ <b>{add_h} ชั่วโมง {add_m} นาที</b><br>
                    <b>ขั้นตอนที่ 3: คำนวณเวลาที่หน้าปัดนาฬิกา</b><br>
                    👉 เริ่มต้น 0{start_h}:00 น. บวกไปอีก {add_h} ชั่วโมง {add_m} นาที<br>
                    👉 จะได้เวลา <b>{ans_h:02d}:{ans_m:02d} น.</b><br>
                    <b>ตอบ: เวลา {ans_h:02d}:{ans_m:02d} น.</b></span>"""
                    
                else: # run
                    if is_challenge:
                        name_samples = random.sample(NAMES, 3)
                        n1 = name_samples[0]
                        n2 = name_samples[1]
                        n3 = name_samples[2]
                        
                        time_choices = [8, 12, 15, 20, 24]
                        time_samples = random.sample(time_choices, 3)
                        t1 = time_samples[0]
                        t2 = time_samples[1]
                        t3 = time_samples[2]
                        
                        lcm = lcm_multiple(t1, t2, t3)
                        
                        q = f"<b>{n1}</b>, <b>{n2}</b>, และ <b>{n3}</b> วิ่งรอบสนามแข่ง 1 รอบ ใช้เวลา <b>{t1} นาที</b>, <b>{t2} นาที</b>, และ <b>{t3} นาที</b> ตามลำดับ<br>ถ้าทั้งสามคนออกสตาร์ทพร้อมกัน พวกเขาจะวิ่งมาเจอกันที่ 'จุดเริ่มต้น' พร้อมกันอีกครั้งในอีกกี่นาที?"
                        div_table = generate_short_division_html([t1, t2, t3], mode="ค.ร.น.")
                    else:
                        name_samples = random.sample(NAMES, 2)
                        n1 = name_samples[0]
                        n2 = name_samples[1]
                        
                        time_choices = [4, 6, 8, 10, 12, 15]
                        time_samples = random.sample(time_choices, 2)
                        t1 = time_samples[0]
                        t2 = time_samples[1]
                        
                        lcm = lcm_multiple(t1, t2)
                        
                        q = f"<b>{n1}</b> และ <b>{n2}</b> วิ่งรอบสนามแข่ง 1 รอบ ใช้เวลา <b>{t1} นาที</b> และ <b>{t2} นาที</b> ตามลำดับ<br>ถ้าทั้งสองคนออกสตาร์ทพร้อมกัน พวกเขาจะวิ่งมาเจอกันที่ 'จุดเริ่มต้น' อีกครั้งในอีกกี่นาที?"
                        div_table = generate_short_division_html([t1, t2], mode="ค.ร.น.")
                        
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (โจทย์ปัญหา ค.ร.น.):</b><br>
                    โจทย์การวิ่งวนรอบสนามแล้วกลับมาเจอกันที่เดิม คือโจทย์ <b>ค.ร.น. (ตัวคูณร่วมน้อย)</b> คลาสสิก<br>
                    <b>ขั้นตอนที่ 1: ตั้งหารสั้นเพื่อหาจุดร่วม</b><br>
                    {div_table}
                    <b>ขั้นตอนที่ 2: สรุปผล</b><br>
                    👉 ค.ร.น. ที่คำนวณได้คือ <b>{lcm} นาที</b><br>
                    👉 นั่นหมายความว่า ต้องใช้เวลาวิ่งวนไปเรื่อยๆ จนครบ {lcm} นาที ทุกคนจึงจะมาครบรอบที่จุดสตาร์ทพร้อมกันพอดี<br>
                    <b>ตอบ: อีก {lcm} นาที</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาเศษส่วนประยุกต์":
                scenario = random.choice(["book", "money", "pole"])
                
                if scenario == "book":
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
                elif scenario == "money":
                    total_choices = [1200, 2400, 3600, 4800, 6000]
                    total = random.choice(total_choices)
                    den1 = 3
                    den2 = 4
                    num1 = 1
                    num2 = 1
                    
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
                    tot_m_choices = [12, 15, 18, 24, 30]
                    tot_m = random.choice(tot_m_choices)
                    
                    f_mud = get_vertical_fraction(1, 3)
                    
                    if tot_m % 4 == 0:
                        f_water = get_vertical_fraction(1, 4)
                        water_part = tot_m // 4
                    else:
                        f_water = get_vertical_fraction(1, 6)
                        water_part = tot_m // 6
                        
                    mud_part = tot_m // 3
                    air_part = tot_m - (mud_part + water_part)
                    
                    q = f"เสาไม้ต้นหนึ่งยาว <b>{tot_m} เมตร</b> ปักอยู่ในสระบัว<br>ส่วนที่จมอยู่ในโคลนคิดเป็น <b>{f_mud} ของความยาวทั้งต้น</b><br>ส่วนที่แช่อยู่ในน้ำคิดเป็น <b>{f_water} ของความยาวทั้งต้น</b><br>จงหาว่าเสาไม้มีส่วนที่โผล่พ้นน้ำขึ้นมากี่เมตร?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาความยาวส่วนที่จมโคลน</b><br>
                    👉 นำความยาวเต็มต้นไปคูณเศษส่วน: <b>{mud_part} เมตร</b><br>
                    <b>ขั้นตอนที่ 2: หาความยาวส่วนที่แช่น้ำ</b><br>
                    👉 (โจทย์บอกว่าของทั้งต้น ไม่ใช่ของที่เหลือ): <b>{water_part} เมตร</b><br>
                    <b>ขั้นตอนที่ 3: หาความยาวส่วนที่โผล่พ้นน้ำ</b><br>
                    👉 นำความยาวเต็ม ลบด้วยส่วนที่จมไปแล้ว: {tot_m} - ({mud_part} + {water_part}) = <b>{air_part} เมตร</b><br>
                    <b>ตอบ: {air_part} เมตร</b></span>"""

            elif actual_sub_t == "สถิติและค่าเฉลี่ย":
                scenario = random.choice(["new_friend", "exam_target"])
                if scenario == "new_friend":
                    count1 = random.randint(3, 8)
                    avg1 = random.randint(25, 55)
                    count2 = count1 + 1
                    avg2 = avg1 + random.randint(2, 6)
                    new_item = (count2 * avg2) - (count1 * avg1)
                    
                    q = f"กลุ่มของ<b>{name}</b>มีสมาชิก <b>{count1} คน</b> มีน้ำหนักตัว 'เฉลี่ย' อยู่ที่ <b>{avg1} กิโลกรัม</b><br>ต่อมามีเพื่อนเดินมาขอเข้ากลุ่มเพิ่มอีก 1 คน ทำให้น้ำหนักเฉลี่ยของกลุ่มเปลี่ยนไปกลายเป็น <b>{avg2} กิโลกรัม</b><br>จงหาว่าเพื่อนคนที่เดินเข้ามาใหม่ มีน้ำหนักกี่กิโลกรัม?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (ย้อนกลับหาผลรวม):</b><br>
                    <b>ขั้นตอนที่ 1: หาผลรวมน้ำหนักของกลุ่มเดิม ({count1} คน)</b><br>
                    👉 ตั้งสมการกลุ่มเดิม: {avg1} × {count1} = <b>{count1 * avg1} กิโลกรัม</b><br>
                    <b>ขั้นตอนที่ 2: หาผลรวมน้ำหนักของกลุ่มใหม่ ({count2} คน)</b><br>
                    👉 ตั้งสมการกลุ่มใหม่: {avg2} × {count2} = <b>{count2 * avg2} กิโลกรัม</b><br>
                    <b>ขั้นตอนที่ 3: หาน้ำหนักของคนที่เข้ามาเพิ่ม</b><br>
                    👉 ผลรวมกลุ่มใหม่ - ผลรวมกลุ่มเดิม: {count2 * avg2} - {count1 * avg1} = <b>{new_item} กิโลกรัม</b><br>
                    <b>ตอบ: {new_item} กิโลกรัม</b></span>"""
                else:
                    exams = random.randint(3, 5)
                    target_avg = random.randint(75, 95)
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
                    q = f"<b>{name}</b> สอบไปแล้ว <b>{exams} วิชา</b> ได้คะแนนดังนี้: <b>{scores_str} คะแนน</b><br>เขาเหลือสอบอีก 1 วิชาสุดท้าย หากต้องการให้คะแนน <b>'เฉลี่ย'</b> ของทุกวิชารวมกันเป็น <b>{target_avg} คะแนน</b> พอดี<br>วิชาสุดท้ายเขาต้องสอบให้ได้กี่คะแนน?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (เป้าหมายค่าเฉลี่ย):</b><br>
                    <b>ขั้นตอนที่ 1: หาคะแนนรวมเป้าหมายทั้งหมด ({exams+1} วิชา)</b><br>
                    👉 {target_avg} × {exams+1} = <b>{total_needed} คะแนน</b><br>
                    <b>ขั้นตอนที่ 2: หาคะแนนรวมที่มีอยู่ในมือตอนนี้ ({exams} วิชา)</b><br>
                    👉 นำคะแนนที่สอบผ่านไปแล้วมาบวกกัน: {' + '.join(map(str, current_scores))} = <b>{current_sum} คะแนน</b><br>
                    <b>ขั้นตอนที่ 3: หาคะแนนวิชาสุดท้ายที่ต้องทำเพิ่ม</b><br>
                    👉 เป้าหมาย - สิ่งที่มีอยู่: {total_needed} - {current_sum} = <b>{needed} คะแนน</b><br>
                    <b>ตอบ: {needed} คะแนน</b></span>"""

            elif actual_sub_t == "ปริมาตรและความจุ":
                scenario = random.choice(["fish_tank", "pour_water", "cube_arrange", "water_leak"])
                
                if scenario == "fish_tank":
                    w = random.randint(5, 12)
                    l = random.randint(10, 25)
                    h = random.randint(10, 20)
                    
                    water_h = random.randint(2, h-3)
                    fill_vol = w * l * (h - water_h)
                    
                    q = f"ตู้ปลาทรงสี่เหลี่ยมมุมฉาก กว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b> <br>ตอนนี้มีน้ำบรรจุอยู่ในตู้ โดยวัดระดับความสูงของน้ำได้ <b>{water_h} ซม.</b><br>จะต้องเติมน้ำลงไปอีกกี่ <b>ลูกบาศก์เซนติเมตร</b> น้ำจึงจะเต็มตู้ปลาพอดี?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาความสูงของน้ำที่ต้องเติมเพิ่ม</b><br>
                    👉 ตู้สูง {h} ซม. มีน้ำอยู่ {water_h} ซม. ➔ ส่วนที่ยังว่าง = {h} - {water_h} = <b>{h - water_h} ซม.</b><br>
                    <b>ขั้นตอนที่ 2: คำนวณปริมาตรน้ำที่ต้องเติมลงไปในช่องว่าง</b><br>
                    👉 กว้าง({w}) × ยาว({l}) × สูงของส่วนที่ว่าง({h - water_h})<br>
                    👉 {w} × {l} × {h - water_h} = <b>{fill_vol:,} ลบ.ซม.</b><br>
                    <b>ตอบ: {fill_vol:,} ลูกบาศก์เซนติเมตร</b></span>"""
                elif scenario == "pour_water":
                    jug_choices = [200, 250, 400, 500]
                    jug = random.choice(jug_choices)
                    tank_l = random.randint(8, 20)
                    ans = (tank_l * 1000) // jug
                    q = f"ถังน้ำใบหนึ่งมีความจุ <b>{tank_l} ลิตร</b> ถ้านำเหยือกที่มีความจุ <b>{jug} มิลลิลิตร</b> <br>ตักน้ำใส่ถังใบนี้ที่กำลังว่างเปล่าจนกว่าจะเต็มถังพอดี จะต้องตักน้ำทั้งหมดกี่ครั้ง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: แปลงความจุของถัง (ลิตร ➔ มิลลิลิตร)</b><br>
                    👉 {tank_l} ลิตร = {tank_l} × 1,000 = <b>{tank_l * 1000:,} มิลลิลิตร</b><br>
                    <b>ขั้นตอนที่ 2: คำนวณหาจำนวนครั้งที่ต้องตัก</b><br>
                    👉 {tank_l * 1000:,} ÷ {jug} = <b>{ans} ครั้ง</b><br>
                    <b>ตอบ: {ans} ครั้ง</b></span>"""
                elif scenario == "cube_arrange":
                    cube_side_choices = [2, 3, 4, 5]
                    cube_side = random.choice(cube_side_choices)
                    w_c = random.randint(3, 6)
                    l_c = random.randint(4, 8)
                    h_c = random.randint(2, 5)
                    
                    w = w_c * cube_side
                    l = l_c * cube_side
                    h = h_c * cube_side
                    total_cubes = w_c * l_c * h_c
                    
                    q = f"กล่องทรงสี่เหลี่ยมมุมฉาก มีความกว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b><br>ถ้านำ <b>'ลูกบาศก์'</b> ที่มีความยาวด้านละ <b>{cube_side} ซม.</b> มาเรียงใส่กล่องใบนี้จนเต็ม<br>จะต้องใช้ลูกบาศก์ทั้งหมดกี่ลูก?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: หาว่าแต่ละด้านสามารถวางลูกบาศก์ได้กี่ลูก</b><br>
                    👉 ด้านกว้าง: {w} ÷ {cube_side} = <b>{w_c} ลูก</b><br>
                    👉 ด้านยาว: {l} ÷ {cube_side} = <b>{l_c} ลูก</b><br>
                    👉 ด้านสูง: {h} ÷ {cube_side} = <b>{h_c} ชั้น</b><br>
                    <b>ขั้นตอนที่ 2: คำนวณจำนวนลูกบาศก์ทั้งหมด</b><br>
                    👉 {w_c} × {l_c} × {h_c} = <b>{total_cubes:,} ลูก</b><br>
                    <b>ตอบ: {total_cubes:,} ลูก</b></span>"""
                else: # water_leak
                    tank_l = random.randint(100, 300)
                    use_l = random.randint(5, 15)
                    use_ml_choices = [200, 250, 500, 750]
                    use_ml = random.choice(use_ml_choices)
                    days = random.randint(3, 8)
                    total_use_ml = days * ((use_l * 1000) + use_ml)
                    tank_ml = tank_l * 1000
                    rem_ml = tank_ml - total_use_ml
                    rem_l_ans = rem_ml // 1000
                    rem_ml_ans = rem_ml % 1000
                    
                    if rem_ml_ans > 0:
                        ans_txt = f"{rem_l_ans} ลิตร {rem_ml_ans} มิลลิลิตร"
                    else:
                        ans_txt = f"{rem_l_ans} ลิตร"
                    
                    q = f"ถังน้ำใบหนึ่งมีน้ำอยู่เต็มถัง <b>{tank_l} ลิตร</b> ถ้าครอบครัวของ<b>{name}</b> ใช้น้ำเฉลี่ยวันละ <b>{use_l} ลิตร {use_ml} มิลลิลิตร</b><br>เมื่อผ่านไป <b>{days} วัน</b> จะมีน้ำเหลืออยู่ในถังเท่าไร?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นตอนที่ 1: คำนวณปริมาณน้ำที่ใช้ไปทั้งหมดใน {days} วัน</b><br>
                    👉 แปลงน้ำที่ใช้ต่อวันเป็นหน่วยเล็กสุด = <b>{(use_l * 1000) + use_ml:,} มิลลิลิตร/วัน</b><br>
                    👉 ใช้เวลา {days} วัน จะใช้น้ำไป: {days} × {(use_l * 1000) + use_ml:,} = <b>{total_use_ml:,} มิลลิลิตร</b><br>
                    <b>ขั้นตอนที่ 2: คำนวณปริมาณน้ำที่เหลือ</b><br>
                    👉 น้ำตอนแรกมี {tank_l} ลิตร = <b>{tank_ml:,} มิลลิลิตร</b><br>
                    👉 หักลบน้ำที่ใช้ไป: {tank_ml:,} - {total_use_ml:,} = <b>{rem_ml:,} มิลลิลิตร</b><br>
                    <b>ขั้นตอนที่ 3: แปลงกลับเป็นหน่วยผสม</b><br>
                    👉 นำ {rem_ml:,} ÷ 1,000 จะได้ <b>{rem_l_ans} ลิตร</b> และเศษ <b>{rem_ml_ans} มิลลิลิตร</b><br>
                    <b>ตอบ: {ans_txt}</b></span>"""

            elif actual_sub_t == "การแปลงหน่วยและเปรียบเทียบ":
                scenario = random.choice(["compare_dec", "time_convert", "cut_pieces"])
                if scenario == "cut_pieces":
                    c_type = random.choice(["wire", "rice", "water"])
                    
                    if c_type == "wire":
                        u_maj = "เมตร"
                        u_min = "เซนติเมตร"
                        mult = 100
                        item = "ลวด"
                        action = "ตัดแบ่งไปใช้งาน"
                        unit = "เส้น"
                    elif c_type == "rice":
                        u_maj = "กิโลกรัม"
                        u_min = "กรัม"
                        mult = 1000
                        item = "ข้าวสาร"
                        action = "ตักแบ่งใส่ถุง"
                        unit = "ถุง"
                    else:
                        u_maj = "ลิตร"
                        u_min = "มิลลิลิตร"
                        mult = 1000
                        item = "น้ำยาล้างจาน"
                        action = "แบ่งใส่ขวด"
                        unit = "ขวด"
                    
                    total_maj = random.randint(8, 20)
                    total_min = random.randint(10, mult-10)
                    total_val = (total_maj * mult) + total_min
                    
                    pieces = random.randint(3, 8)
                    per_piece_maj = random.randint(0, 1)
                    per_piece_min = random.randint(100, 800)
                    
                    if per_piece_maj == 0 and per_piece_min < (mult//5): 
                        per_piece_min += (mult//2)
                        
                    per_piece_val = (per_piece_maj * mult) + per_piece_min
                    used_val = pieces * per_piece_val
                    
                    while used_val >= total_val:
                        total_maj += 5
                        total_val = (total_maj * mult) + total_min
                        
                    rem_val = total_val - used_val
                    rem_maj = rem_val // mult
                    rem_min = rem_val % mult
                    
                    if per_piece_maj > 0:
                        piece_txt = f"{per_piece_maj} {u_maj} {per_piece_min} {u_min}"
                    else:
                        piece_txt = f"{per_piece_min} {u_min}"
                        
                    if rem_maj > 0:
                        ans_txt = f"{rem_maj} {u_maj} {rem_min} {u_min}"
                    else:
                        ans_txt = f"{rem_min} {u_min}"
                        
                    q = f"<b>{name}</b> มี{item}ทั้งหมด <b>{total_maj} {u_maj} {total_min} {u_min}</b> <br>นำไป{action}จำนวน <b>{pieces} {unit}</b> ({unit}ละเท่าๆ กัน) โดยแต่ละ{unit}ใช้ไป <b>{piece_txt}</b> <br>จะเหลือ{item}อยู่เท่าไร?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นที่ 1: แปลงหน่วยทั้งหมดให้เป็นหน่วยเล็กสุด ({u_min})</b><br>
                    👉 ของที่มีทั้งหมด: ({total_maj} × {mult:,}) + {total_min} = <b>{total_val:,} {u_min}</b><br>
                    👉 ของที่ใช้ต่อ 1 {unit}: ({per_piece_maj} × {mult:,}) + {per_piece_min} = <b>{per_piece_val:,} {u_min}</b><br>
                    <b>ขั้นที่ 2: คำนวณปริมาณที่ใช้ไปทั้งหมด</b><br>
                    👉 ใช้ไป {pieces} {unit}: {pieces} × {per_piece_val:,} = <b>{used_val:,} {u_min}</b><br>
                    <b>ขั้นที่ 3: หาปริมาณที่เหลือ</b><br>
                    👉 {total_val:,} - {used_val:,} = <b>{rem_val:,} {u_min}</b><br>
                    <b>ขั้นที่ 4: แปลงกลับเป็นหน่วยผสม</b><br>
                    👉 นำ {rem_val:,} ÷ {mult:,} จะได้ <b>{rem_maj} {u_maj}</b> และเศษ <b>{rem_min} {u_min}</b><br>
                    <b>ตอบ: {ans_txt}</b></span>"""
                
                elif scenario == "time_convert":
                    days = random.randint(2, 5)
                    hours = random.randint(5, 20)
                    total_h = days * 24 + hours
                    
                    diff_h_choices = [-10, -5, 5, 10]
                    diff_h = random.choice(diff_h_choices)
                    compare_h = total_h + diff_h
                    
                    if total_h > compare_h:
                        ans_txt = f"รอบที่ 1 นานกว่าอยู่ {total_h - compare_h} ชั่วโมง"
                    else:
                        ans_txt = f"รอบที่ 2 นานกว่าอยู่ {compare_h - total_h} ชั่วโมง"
                    
                    q = f"การเดินทางรอบที่ 1 ใช้เวลา <b>{days} วัน {hours} ชั่วโมง</b> <br>การเดินทางรอบที่ 2 ใช้เวลา <b>{compare_h} ชั่วโมง</b><br>จงเปรียบเทียบว่าการเดินทางรอบใดใช้เวลา <b>นานกว่ากัน</b> และนานกว่ากันกี่ชั่วโมง?"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step (การแปลงหน่วยเวลา):</b><br>
                    <b>ขั้นที่ 1: แปลงหน่วยของรอบที่ 1 ให้เป็น 'ชั่วโมง' ล้วนๆ</b><br>
                    👉 {days} วัน = {days} × 24 = <b>{days * 24} ชั่วโมง</b><br>
                    👉 นำไปรวมกับเศษชั่วโมงเดิม: {days * 24} + {hours} = <b>{total_h} ชั่วโมง</b><br>
                    <b>ขั้นที่ 2: เปรียบเทียบตัวเลข</b><br>
                    👉 รอบที่ 1: {total_h} ชั่วโมง | รอบที่ 2: {compare_h} ชั่วโมง<br>
                    👉 นำมาลบกันหาผลต่าง: | {total_h} - {compare_h} | = <b>{abs(total_h - compare_h)} ชั่วโมง</b><br>
                    <b>ตอบ: {ans_txt}</b></span>"""
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
                    is_plus = random.choice([True, False])
                    
                    if is_plus:
                        val_B_minor_total = val_A_minor_total + diff_amount
                    else:
                        val_B_minor_total = val_A_minor_total - diff_amount
                    
                    is_A_left = random.choice([True, False])
                    if is_A_left:
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
                        
                    if selected_type == "kg_g":
                        comp_word = "หนักกว่า"
                    elif selected_type == "m_cm":
                        comp_word = "ยาวกว่า"
                    else:
                        comp_word = "ไกลกว่า"
                        
                    if val_A > val_B:
                        word_ans = "ฝั่งซ้าย มากกว่า"
                        sign = ">"
                    else:
                        word_ans = "ฝั่งขวา มากกว่า"
                        sign = "<"
                    
                    q = f"จงเปรียบเทียบว่า <b>{item_A}</b> กับ <b>{item_B}</b> สิ่งใดมีค่ามากกว่ากัน?<br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีคิดวิเคราะห์แบบ Step-by-Step:</b><br>
                    <b>ขั้นที่ 1: ทบทวนความสัมพันธ์ของหน่วย</b><br>
                    👉 1 {u_major} เท่ากับ <b>{multiplier:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: แปลงหน่วยให้เหมือนกัน (แปลง {u_major} เป็น {u_minor})</b><br>"""
                    if is_a_major:
                        sol += f"👉 ฝั่งซ้าย: {val_A_major} {u_major} = {val_A_major} × {multiplier:,} = <b>{val_A_minor_total:,} {u_minor}</b><br>👉 ฝั่งขวา: คือ <b>{val_B_minor_total:,} {u_minor}</b><br>"
                    else:
                        sol += f"👉 ฝั่งซ้าย: คือ <b>{val_B_minor_total:,} {u_minor}</b><br>👉 ฝั่งขวา: {val_A_major} {u_major} = {val_A_major} × {multiplier:,} = <b>{val_A_minor_total:,} {u_minor}</b><br>"
                    sol += f"<b>ขั้นที่ 3: เปรียบเทียบตัวเลข</b><br>👉 จะเห็นว่า <b>{val_A:,} {sign} {val_B:,}</b><br><b>ตอบ: {word_ans}</b></span>"

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
            html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับแสดงวิธีคิดวิเคราะห์...</div><div class="ans-line">ตอบ: </div>'
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
            header_color = "#e67e22"
        else:
            bg_color = "#525659"
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
    st.success(f"✅ โค้ดฉบับเต็ม 1,300+ บรรทัดสมบูรณ์แล้วครับ! รื้อระบบการสุ่มตัวเลขใหม่ทั้งหมด ไม่จำเจแน่นอน และครอบคลุมโจทย์ปัญหาทั้ง 4 แบบในหมวดปริมาตรครับ")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
