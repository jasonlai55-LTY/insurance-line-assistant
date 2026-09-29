import os
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_proposal_docx(filename):
    doc = Document()

    # 設定頁邊距
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # 設置預設字型名稱
    doc.styles['Normal'].font.name = '微軟正黑體'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
    doc.styles['Normal'].font.size = Pt(11)
    doc.styles['Normal'].font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # 主標題
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(6)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("保險業務員 LINE 助手\n內部極速上線實務手冊與呈報規劃")
    run_title.font.name = "微軟正黑體"
    run_title._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79) # 深藍

    # 副標題
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(20)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("針對保險公司內勤與通路單位之「免連核心、解耦架構、資安安心、小步快跑」落地指南")
    run_sub.font.name = "微軟正黑體"
    run_sub._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    # 分隔線
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_after = Pt(16)
    r_hr = p_hr.add_run("―" * 42)
    r_hr.font.color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
    p_hr.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(8)
        run = h.add_run(text)
        run.font.name = "微軟正黑體"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        run = h.add_run(text)
        run.font.name = "微軟正黑體"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
        return h

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = "微軟正黑體"
            r_b._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
            r_b.font.bold = True
            r_b.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        r_t = p.add_run(text)
        r_t.font.name = "微軟正黑體"
        r_t._element.rPr.rFonts.set(qn('w:eastAsia'), '微軟正黑體')
        return p

    # --- 1. 專案定位與核心優勢 ---
    add_heading_1("一、 專案定位與核心優勢 (Executive Summary)")
    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_after = Pt(8)
    p_desc.add_run("本專案「保險業務員 LINE 助手」定位為提供給保險公司通路內勤、督導區及通訊處使用的輕量化數位作業工具。專案採用解耦架構設計，能在不改動總公司核心主機 (Core System) 的前提下，於極短時間內完成內部上線並發揮效益。")

    add_bullet(" 採用 Excel 批次作業與全自動個資掩碼 (Data Masking)，完全不需要開啟核心資料庫防火牆通道，免去漫長審核。", "1. 零核心系統負擔：")
    add_bullet(" 自動隱碼關鍵個資（身分證字號、手機），杜絕資安漏洞與法遵開罰風險。", "2. 高度資安防護：")
    add_bullet(" 上架商品 DM、5大行政規範表單（投保、保費、保全、理賠、各式表單）與多選分眾廣播通知，業務員隨手可查。", "3. 業務員端秒查體驗：")

    # --- 2. 內部極速上線 4 大實務步驟 ---
    add_heading_1("二、 公司內部極速上線 4 大步驟 (Internal Rollout Roadmap)")

    add_heading_2("步驟一：架設「部門專屬測試/營運主機」（繞過總公司漫長排程）")
    add_bullet("向部門申請一台連線至公司內部網路的獨立閒置電腦或虛擬機 (VM)。", "資源取得：")
    add_bullet("使用專案內建之 Docker 容器化配置，5 分鐘內完成 FastAPI 後端、PostgreSQL 與 Vue 3 管理後台的部署。", "極速部署：")
    add_bullet("部門內勤直接在瀏覽器輸入內部 IP (如 http://10.x.x.x:3001) 即可操作；業務員端則透過 Cloudflare 通道以 LINE 順暢開啟。", "存取方式：")

    add_heading_2("步驟二：準備「主管資安安心與呈報說明」（消除高層後顧之憂）")
    p_s2 = doc.add_paragraph()
    p_s2.paragraph_format.space_after = Pt(6)
    p_s2.add_run("向部門副總或高層匯報時，針對主管最關心的個資與資安議題，直接提供 3 大安心保證：")
    add_bullet("系統內建 Data Masking 機制，敏感個資發送前與資料庫內皆經資安掩碼處理，完全符合資安法規。", "保證 1【零個資風險】：")
    add_bullet("採 Excel 批次作業解耦架構，絕不連接總公司核心資料庫，不會影響核心主機穩定性。", "保證 2【零核心主機風險】：")
    add_bullet("內部核保與特批規範採 OTP 身分驗證機制，非驗證業務員無法存取限閱文件。", "保證 3【權限分級防護】：")

    add_heading_2("步驟三：實施「單一單位 Pilot 試行」（用數據成果說話）")
    add_bullet("選擇 1~2 個績效好、業務量大且積極的地方通訊處（如：台北一處），邀請行政內勤與處經理率先體驗試用。", "試行單位：")
    add_bullet("內勤使用後台發送行政照會與商品 DM，業務員使用 LINE 手機端即時接收與查詢。", "試行內容：")
    add_bullet("試行 2 週後收集數據：「照會發送處理時間由 2 小時大幅縮短至 3 分鐘，業務員 DM 查找率提升 90%」。", "效益收集：")

    add_heading_2("步驟四：製作「內勤一頁式圖解指南」並全通路擴展")
    add_bullet("準備 1 頁簡單 PDF 指南（包含後台登入、Excel 範本下載、匯入發送 3 步驟），分發給其他通訊處內勤同仁，順理成章推廣至全公司。", "推廣落地：")

    # --- 3. 資安與法遵問答對照表 ---
    add_heading_1("三、 資安與法遵審查問答對照表 (Compliance Checklist)")

    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # 表頭顏色
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "資安/法遵審查項目"
    hdr_cells[1].text = "本系統對應之資安防護設計"
    for cell in hdr_cells:
        set_cell_background(cell, "1F4E79")
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    items = [
        ("個資保護與去識別化", "內建 Data Masking 自動脫敏機制，身分證字號與手機號碼發送前自動去識別化掩碼，避免任何洩漏個資風險。"),
        ("存取權限控管 (RBAC)", "區分「公開素材」與「內部限閱文件」，業務員需通過 OTP 身分驗證後，方可存取核保與特批規範。"),
        ("核心系統相容性", "採用獨立隔離之 Excel 批次解耦架構，無需與公司核心主機硬連線，杜絕資安攻擊滲透主機之風險。")
    ]

    for i, (col1, col2) in enumerate(items, start=1):
        row_cells = table.rows[i].cells
        row_cells[0].text = col1
        row_cells[1].text = col2
        if i % 2 == 1:
            set_cell_background(row_cells[0], "F2F2F2")
            set_cell_background(row_cells[1], "F2F2F2")

    # --- 4. 系統核心功能與組織架構 ---
    add_heading_1("四、 系統核心功能與架構亮點 (Key Features)")
    add_bullet("通路 >> 督導區/區部 >> 通訊處/單位 >> 職級 (支援外部通路彈性欄位選填)。", "1. 四階層組織架構：")
    add_bullet("包含「全部規範與表單」、「投保規則」、「保費規則」、「保全規則」、「理賠注意事項」、「各式表單」。", "2. 5 大行政規範分類：")
    add_bullet("支援依職級、督導區、通訊處多選複選廣播，與個人通知中心訊息歷史紀錄。", "3. 複選分眾廣播中心：")
    add_bullet("業務員主資料、分眾標籤、素材表單、推播照會全數提供「一鍵批次匯入」與「標準空白範本檔 (.xlsx) 下載」。", "4. 全模組 Excel 自動化：")

    # --- 5. 結論 ---
    add_heading_1("五、 結論 (Conclusion)")
    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_before = Pt(6)
    p_concl.add_run("本專案已跨越最困難的「原型開發與邏輯調校」階段。透過「解耦上線 + 部門 Pilot 試行」的策略，可在零資安風險、免等待 IT 漫長排程的前提下，於最短時間內在公司內部正式上線，成為協助內勤極速減負、提升業務員效率的數位轉型亮眼成果。")

    doc.save(filename)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    out_file = "保險業務員LINE助手_內部極速上線實務手冊與呈報規劃.docx"
    create_proposal_docx(out_file)
