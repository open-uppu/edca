# EDCA & AI Weekly Investment Advisor

ระบบคำนวณและวางแผนการลงทุนแบบ **Enhanced Dollar-Cost Averaging (EDCA)** แบบ Multi-Factor พร้อม **AI Weekly Investment Advisor** เชื่อมต่อกับ LLM Gateway (`http://100.105.249.12:4000`)

## คุณสมบัติหลัก
1. **Multi-Factor Dynamic Multiplier ($M_t \in [0.5, 2.0]$)**:
   - ปรับยอดเงินลงทุนรายสัปดาห์จากงบฐาน 1,000 บาท (500 – 2,000 บาท)
   - ปัจจัย: 200 EMA (Trend), Drawdown from ATH (ส่วนลดราคา), RSI(14) (Momentum)
2. **Cash Buffer Reserve Pool**:
   - พักเงินส่วนต่างในสัปดาห์ที่ตลาดแพง
   - ดึงเงินสำรองมาช้อนซื้อในสัปดาห์ที่ตลาดลดราคา
3. **Market Holiday Engine**:
   - ตรวจจับปฏิทินวันหยุดตลาดสหรัฐฯ (NYSE) และตลาดหุ้นไทย (SET)
   - เลือกวันส่งคำสั่งที่สภาพคล่องดีที่สุด (วันพุธ หรือ วันอังคาร 21:45 น.)
4. **Dime! Portfolio Integration & Rebalancer**:
   - ล็อกหุ้น Overweight (TSM, ARM, SCB) เพื่อลดความเสี่ยงกระจุกตัว
   - คัดเลือกหุ้นคุณภาพดีที่มีส่วนลด (เช่น GOOGL, TSLA, DELTA, BDMS)
5. **AI Weekly Advisor**:
   - สังเคราะห์คำแนะนำภาษาไทยผ่าน LLM Gateway `100.105.249.12:4000` (โมเดล `auto`)

## การใช้งาน CLI
```bash
# รันคำแนะนำการลงทุนประจำสัปดาห์
python3 cli.py recommend

# ดูสรุปพอร์ต Dime! และสถานะความเสี่ยง
python3 cli.py portfolio

# รัน Simulator จำลองผลตอบแทน EDCA vs Static DCA
python3 cli.py backtest
```

## การรันชุดทดสอบ (Unit Tests)
```bash
pytest tests/ -v
```
