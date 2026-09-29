import re

class DataMaskingService:
    """
    資安與合規底線：個資脫敏掩碼處理器
    - 嚴禁包含完整客戶姓名、身分證字號或病歷/保單資訊。
    """
    
    @staticmethod
    def mask_name(name: str) -> str:
        """
        姓名脫敏：
        - 兩字中文：張三 -> 張*
        - 三字以上中文：張大明 -> 張*明, 諸葛孔明 -> 諸**明
        - 英文：John Smith -> J*** S****
        """
        if not name:
            return ""
        name = name.strip()
        if re.search(r'[\u4e00-\u9fa5]', name):
            # 中文姓名
            if len(name) <= 2:
                return name[0] + "*"
            else:
                return name[0] + "*" * (len(name) - 2) + name[-1]
        else:
            # 英文姓名
            parts = name.split()
            masked_parts = []
            for part in parts:
                if len(part) <= 1:
                    masked_parts.append(part)
                else:
                    masked_parts.append(part[0] + "*" * (len(part) - 1))
            return " ".join(masked_parts)

    @staticmethod
    def mask_tw_id(id_str: str) -> str:
        """
        台灣身分證字號脫敏：
        - A123456789 -> A12****789
        """
        if not id_str:
            return ""
        pattern = r'([A-Z][12]\d)\d{4}(\d{3})'
        return re.sub(pattern, r'\1****\2', id_str)

    @staticmethod
    def mask_policy_number(policy_no: str) -> str:
        """
        保單號碼脫敏：
        - P987654321 -> P98****321
        """
        if not policy_no or len(policy_no) < 6:
            return policy_no
        prefix = policy_no[:3]
        suffix = policy_no[-3:]
        mask_len = len(policy_no) - 6
        return f"{prefix}{'*' * max(mask_len, 4)}{suffix}"

    @classmethod
    def sanitize_text(cls, raw_text: str) -> str:
        """
        全內文自動個資掃描與脫敏：
        過濾身分證、保單號碼、客戶姓名常見標籤語法 (例如：客戶：張大明，身分證：A123456789，保單號碼：P987654321)
        """
        if not raw_text:
            return ""
        
        text = raw_text
        
        # 1. 替換台灣身分證字號
        tw_id_regex = r'[A-Z][12]\d{8}'
        matches = re.findall(tw_id_regex, text)
        for match in set(matches):
            text = text.replace(match, cls.mask_tw_id(match))

        # 2. 替換指定標籤後的客戶姓名
        # 例如："客戶: 張大明", "保戶：李小龍"
        customer_label_regex = r'(客戶[：:]\s*|保戶[：:]\s*)([\u4e00-\u9fa5]{2,4}|[A-Za-z\s]+)'
        def replace_customer(match):
            label = match.group(1)
            name = match.group(2)
            return label + cls.mask_name(name)
        text = re.sub(customer_label_regex, replace_customer, text)

        # 3. 替換指定標籤後的保單號碼
        policy_label_regex = r'(保單號碼[：:]\s*|保單編號[：:]\s*)([A-Za-z0-9\-]{6,15})'
        def replace_policy(match):
            label = match.group(1)
            p_no = match.group(2)
            return label + cls.mask_policy_number(p_no)
        text = re.sub(policy_label_regex, replace_policy, text)

        return text
