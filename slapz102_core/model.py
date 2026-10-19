import copy

from bson.objectid import ObjectId

class mongo_model:

    def __init__(self, record, lookup, db_handle):
        self._mongo_record = copy.deepcopy(record)
        self._lookup_record = copy.deepcopy(lookup)
        self._db_handle = db_handle
    # end def

    def put(self, key, value):
        if not (key in self._lookup_record):
            raise ValueError("SETTING_NON_EXISTING_FIELD", key, value)
        # end if
        self._mongo_record[key] = value
    # end def

    def get(self):
        return self._mongo_record
    # end def

    def delete(self, query):
        collection_name = self._lookup_record["__db__name__"]
        self._db_handle[collection_name].remove(query)
    # end def

    def insert(self, lock=None):
        collection_name = self._lookup_record["__db__name__"]
        del self._mongo_record["__db__name__"]
        if lock == None:
            self._db_handle[collection_name].insert_one(
                self._mongo_record
            )
        else:
            self._db_handle[collection_name].insert_one(
                self._mongo_record,
                session=lock
            )
        # end if
    # end def

    def update(self, query):
        collection_name = self._lookup_record["__db__name__"]
        self._db_handle[collection_name].update(
            query,
            {"$set": self._mongo_record}
        )
    # end def
# end class

db = {

    "db_unique_counter": {
        "counter": 0,
    },

    "db_config": {
        "_id": ObjectId(),
        "name": "",
        "value": "",
        "desc": "",
        "config_type": "",
        "misc": "",
        "data": {}
    },

    "db_site": {
        "name": "",
        "event_name": "",
        "event_full_name": "",
        "graduation_year": "",
        "class_label": "",
        "tagline": "",
        "tagline_id": "",
        "presented_by": "",
        "presented_by_id": "",
        "subtitle": "",
        "subtitle_id": "",
        "description": "",
        "description_id": "",
        "phone": "",
        "whatsapp_url": "",
        "announcement": "",
        "announcement_id": "",
        "contribution": "",
        "contribution_num": 2000000,
        "shipping_minimum_progress_num": 100000,
        "shipping_service_fee_num": 10000,
        "merch_general_discount_pct": 0,
        "merch_referral_discount_pct": 0,
        "merch_discount_note": "",
        "about_fraco": "",
        "about_purpose": "",
        "about_audience": "",
        "about_activities": "",
        "about_impact": "",
        "status": "ENABLE"
    },

    "db_product": {
        "slug": "",
        "name": "",
        "price": "",
        "price_num": 0,
        "bahan_baku": "",
        "bahan_baku_num": 0,
        "profit": "",
        "profit_num": 0,
        "image": "",
        "images": [],
        "description": "",
        "sizes": [],
        "colors": [],
        "category": "",
        "availability": "",
        "is_preorder": False,
        "allow_preorder": False,
        "preorder_eta": "",
        "preorder_note": "",
        "stock": 0,
        "stock_by_size": {},
        "sku": "",
        "discount": "",
        "discount_type": "PCT",
        "discount_num": 0,
        "discount_note": "",
        "discount_enabled": False,
        "reserved": 0,
        "sold": 0,
        "status": "ACTIVE"
    },

    "db_program": {
        "slug": "",
        "title": "",
        "description": "",
        "image": "",
        "about": "",
        "venue": "",
        "venue_mode": "OFFLINE",
        "venue_url": "",
        "cta_label": "",
        "cta_href": "",
        "topics": [],
        "industries": [],
        "order": 0,
        "status": "PUBLISHED"
    },

    "db_update": {
        "slug": "",
        "title": "",
        "date": "",
        "category": "",
        "excerpt": "",
        "image": "",
        "content": "",
        "author": "",
        "fk_program_slug": "",
        "status": "PUBLISHED"
    },

    "db_gallery": {
        "image": "",
        "alt": "",
        "album": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_timeline": {
        "month": "",
        "items": [],
        "order": 0,
        "status": "ENABLE"
    },

    "db_division": {
        "name": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_user": {
        "fk_user_id": "",
        "username": "",
        "password": "",
        "role": "PARTICIPANT",
        "name": "",
        "phone": "",
        "email": "",
        "status": "ENABLE"
    },

    "db_order": {
        "order_id": "",
        "fk_user_id": "",
        "session_id": "",
        "items": [],
        "subtotal": "",
        "subtotal_num": 0,
        "bahan_baku_total": "",
        "bahan_baku_total_num": 0,
        "profit_total": "",
        "profit_total_num": 0,
        "has_preorder": False,
        "preorder_eta": "",
        "shipping": "",
        "shipping_num": 0,
        "shipping_handler": "",
        "shipping_recipient_same_buyer": True,
        "shipping_name": "",
        "shipping_phone": "",
        "shipping_address": "",
        "shipping_street": "",
        "shipping_address_detail": "",
        "shipping_province": "",
        "shipping_province_id": "",
        "shipping_city": "",
        "shipping_city_id": "",
        "shipping_district": "",
        "shipping_district_id": "",
        "shipping_village": "",
        "shipping_village_id": "",
        "shipping_postal_code": "",
        "shipping_package_note": "",
        "shipping_request_status": "NOT_REQUESTED",
        "shipping_expedition": "",
        "shipping_budget": "",
        "shipping_budget_num": 0,
        "shipping_service_fee": "",
        "shipping_service_fee_num": 0,
        "shipping_tracking_code": "",
        "shipping_tracking_url": "",
        "discount_general_pct": 0,
        "discount_general_num": 0,
        "discount_referral_pct": 0,
        "discount_referral_num": 0,
        "discount_total": "",
        "discount_total_num": 0,
        "total": "",
        "total_num": 0,
        "referral_code": "",
        "fk_referrer_id": "",
        "fk_referrer_reg_id": "",
        "full_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "street": "",
        "address_detail": "",
        "province": "",
        "province_id": "",
        "city": "",
        "city_id": "",
        "district": "",
        "district_id": "",
        "village": "",
        "village_id": "",
        "postal_code": "",
        "notes": "",
        "payment_status": "Pending",
        "order_status": "Pending Payment",
        "fk_receive_account": "",
        "receive_account_label": ""
    },

    "db_cart": {
        "fk_user_id": "",
        "session_id": "",
        "fk_product_id": "",
        "slug": "",
        "qty": 1,
        "size": "",
        "color": ""
    },

    "db_participant": {
        "fk_user_id": "",
        "session_id": "",
        "reg_id": "",
        "member_type": "AHC_MEMBER",
        "full_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "city": "",
        "emergency_contact": "",
        "notes": "",
        "payment_plan": "",
        "shirt_size": "",
        "contribution": "Rp 2.000.000",
        "contribution_num": 2000000,
        "amount_paid": "Rp 0",
        "amount_paid_num": 0,
        "sales_total": "Rp 0",
        "sales_total_num": 0,
        "sales_count": 0,
        "proposal_total": "Rp 0",
        "proposal_total_num": 0,
        "self_contribution": "Rp 0",
        "self_contribution_num": 0,
        "remaining": "Rp 2.000.000",
        "remaining_num": 2000000,
        "referral_code": "",
        "password_hint": "",
        "registration_status": "Pending",
        "payment_status": "Pending",
        "member_kit_status": "Processing"
    },

    "db_faq": {
        "fk_program_slug": "",
        "question": "",
        "answer": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_schedule": {
        "fk_program_slug": "",
        "title": "",
        "time_label": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_university": {
        "name": "",
        "booth": "",
        "description": "",
        "contact_person": "",
        "email": "",
        "phone": "",
        "payment": "",
        "notes": "",
        "status": "PENDING"
    },

    "db_speaker": {
        "name": "",
        "job_title": "",
        "industry": "",
        "bio": "",
        "photo": "",
        "status": "ENABLE"
    },

    "db_activity": {
        "name": "",
        "date": "",
        "time_label": "",
        "location": "",
        "description": "",
        "status": "ENABLE"
    },

    "db_event": {
        "title": "",
        "date": "",
        "location": "",
        "description": "",
        "image": "",
        "time_label": "",
        "venue": "",
        "capacity": "",
        "deadline": "",
        "speaker": "",
        "event_status": "Upcoming",
        "status": "ENABLE"
    },

    "db_program_reg": {
        "fk_program_slug": "",
        "full_name": "",
        "email": "",
        "phone": "",
        "organization": "",
        "city": "",
        "notes": "",
        "booth": "",
        "logo": "",
        "show_campus": False,
        "status": "PENDING"
    },

    "db_sponsor_package": {
        "slug": "",
        "name": "",
        "amount": "",
        "benefits": [],
        "logo_placement": "",
        "booth": "",
        "promo": "",
        "other": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_vendor_category": {
        "name": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_merchandise_category": {
        "name": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_shipping_expedition": {
        "name": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_sponsor_app": {
        "company_name": "",
        "contact_person": "",
        "email": "",
        "phone": "",
        "website": "",
        "industry": "",
        "package_slug": "",
        "collaboration": "",
        "message": "",
        "file_name": "",
        "file_path": "",
        "notes": "",
        "assigned_pic": "",
        "status": "PENDING"
    },

    "db_vendor_app": {
        "business_name": "",
        "contact_person": "",
        "email": "",
        "phone": "",
        "category": "",
        "division": "",
        "description": "",
        "services": "",
        "profile": "",
        "portfolio": "",
        "pricing": "",
        "notes": "",
        "file_name": "",
        "file_path": "",
        "assigned_pic": "",
        "status": "PENDING"
    },

    "db_payment": {
        "fk_user_id": "",
        "fk_reg_id": "",
        "amount": "",
        "amount_num": 0,
        "method": "",
        "note": "",
        "pay_type": "",
        "transaction_kind": "INCOME",
        "source_type": "",
        "source_ref": "",
        "referral_code": "",
        "transaction_date": "",
        "fk_receive_account": "",
        "receive_account_label": "",
        "name": "",
        "email": "",
        "status": "PENDING"
    },

    "db_receive_account": {
        "label": "",
        "bank_name": "",
        "account_number": "",
        "account_holder": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_team": {
        "name": "",
        "position": "",
        "division": "",
        "photo": "",
        "bio": "",
        "social": "",
        "order": 0,
        "status": "ENABLE"
    },

    "db_donation_settings": {
        "title": "Support Us",
        "intro": "",
        "email": "",
        "whatsapp": "",
        "whatsapp_url": "",
        "phone": "",
        "follow_up_note": "",
        "top_limit": 10,
        "list_mode": "LIMIT",
        "public_total_mode": "ACCUMULATED",
        "public_total_num": 0,
        "proposal_pdf_url": "",
        "proposal_pdf_label": "Download proposal (PDF)",
        "status": "ENABLE"
    },

    "db_donor": {
        "name": "",
        "is_anonymous": False,
        "phone": "",
        "amount_label": "",
        "amount_num": 0,
        "score": 0,
        "note": "",
        "referral_code": "",
        "fk_referrer_id": "",
        "fk_referrer_reg_id": "",
        "pledge_source": "",
        "fk_receive_account": "",
        "receive_account_label": "",
        "follow_status": "FOLLOW_UP",
        "status": "HIDDEN"
    }
}
