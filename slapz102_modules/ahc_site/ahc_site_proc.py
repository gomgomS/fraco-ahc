import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_seed import ahc_site_seed

class ahc_site_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    # CMS fields that can switch EN <-> ID (admin Settings). Not for news/events/products.
    LANG_FIELDS = [
        "announcement",
        "tagline",
        "subtitle",
        "description",
        "presented_by",
        "about_fraco",
        "about_purpose",
        "about_audience",
        "about_activities",
        "about_impact"
    ]

    UI = {
        "en": {
            "explore": "Explore FRACO",
            "shop": "Shop Merchandise",
            "about_title": "About FRACO",
            "learn_more": "Learn More",
            "programs_title": "Our Programs",
            "view_all": "View All",
            "merch_title": "Merchandise",
            "shop_all": "Shop All Merchandise",
            "add_cart": "Add to Cart",
            "view": "View",
            "partners_title": "Partners",
            "partners_kicker": "Build it with us",
            "partners_heading": "Let's Build with FRACO",
            "partners_body": "Companies, brands, businesses, and organizations can collaborate with FRACO — class of 2017 — on {event} through sponsorship, vendor services, and university booths.",
            "become_sponsor": "Become a Sponsor",
            "download_proposal": "Download Proposal",
            "updates_title": "Latest Updates",
            "gallery_title": "Gallery",
            "nav_home": "Home",
            "nav_about": "About",
            "nav_support": "Support Us",
            "nav_cart": "Cart",
            "nav_help": "Help",
            "nav_login": "Login",
            "nav_account": "Account",
            "footer_navigate": "Navigate",
            "footer_participate": "Participate",
            "footer_contact": "Contact",
            "search_placeholder": "Search FRACO programs, merch, updates...",
            "search_btn": "Search",
            "search_close": "Close",
            "about_h1": "About",
            "about_community": "The community",
            "about_fraco_heading": "About FRACO",
            "about_ahc_heading": "About Alumni Home Coming",
            "about_activities_title": "Main activities",
            "about_view_programs": "View Programs",
            "about_timeline_title": "Timeline",
            "about_timeline_range": "August 2026 — April 2027",
            "about_timeline_empty": "Timeline will appear here as preparation dates are confirmed.",
            "about_team_title": "Our Team",
            "about_divisions_label": "FRACO divisions",
            "about_division": "Division",
            "about_divisions_empty": "Division listings will appear here.",
            "about_register": "Register",
            "about_explore_programs": "Explore Programs",
            "shop_h1": "Shop",
            "proof_supporting": "Already supporting FRACO",
            "proof_customers": "customers have purchased merchandise",
            "proof_merch_total": "Total merchandise purchased",
            "proof_paid_orders": "paid orders",
            "badge_in_stock": "In stock",
            "badge_out_stock": "Out of stock",
            "badge_preorder": "Preorder",
            "size_kids": "Kids",
            "size_guide_title": "Size guide",
            "size_lebar": "Width",
            "size_panjang": "Length",
            "size_note": "Measurements in cm · tolerance +/-2-3 cm",
            "cart_title": "Bag",
            "cart_continue": "Continue shopping",
            "cart_qty": "Qty",
            "cart_remove": "Remove",
            "cart_subtotal": "Subtotal",
            "cart_shipping": "Shipping",
            "cart_total": "Total",
            "cart_preorder_note": "Includes preorder item(s) · expected {eta}. Payment still confirms the order.",
            "cart_ready_eta": "Ready {eta}",
            "cart_checkout": "Checkout",
            "cart_empty": "Your bag is currently empty.",
            "stamp_paid": "LUNAS",
            "badge_in_stock_cap": "In Stock",
            "badge_out_stock_cap": "Out of Stock",
            "size_one": "One Size",
            "merch_all_products": "All Products",
            "support_anonymous": "Anonymous",
            "support_fallback_name": "FRACO supporter",
            "support_amount_fallback": "Support",
            "merch_preorder_open": "Out of stock · preorder open",
            "merch_ready_ship": "Ready to ship",
            "merch_unavailable": "Unavailable",
            "merch_see_product": "See product",
            "merch_empty_category": "No products in this category yet.",
            "search_label": "Search:",
            "track_kicker": "Order tracking",
            "track_title": "Track your merchandise",
            "track_desc": "Enter the transaction code shown after checkout to see payment, shipping, and merchandise progress.",
            "track_code_label": "Transaction code",
            "track_code_placeholder": "Example: FR1788508509",
            "track_btn": "Track order",
            "track_not_found": "No merchandise order was found for {code}. Check the code and try again.",
            "track_general": "General information",
            "track_total": "Total:",
            "track_payment": "Payment status",
            "track_order": "Order:",
            "track_shipping": "Shipping status",
            "track_expedition": "Expedition:",
            "track_code": "Tracking code:",
            "track_shipment": "Track shipment →",
            "track_cancelled": "This order was cancelled.",
            "track_progress": "Merchandise progress",
            "track_items": "Items",
            "track_preorder_note": "Includes preorder merchandise · expected {eta}.",
            "support_proof_supporters": "supporters have contributed",
            "support_proof_total": "Total support received",
            "support_thanks_line": "Thank you for keeping {event} moving forward",
            "support_top_title": "Top supporters",
            "support_top_desc": "Thank you — friends, family, and Class of {year} classmates who keep {event} moving forward.",
            "support_donor_label": "Support",
            "support_donors_empty": "Supporters will appear here soon.",
            "support_contact_email": "Email",
            "support_contact_whatsapp": "WhatsApp",
            "support_contact_phone": "Phone",
            "support_chat_whatsapp": "Chat on WhatsApp",
            "support_whatsapp_us": "WhatsApp us",
            "support_email_us": "Email us",
            "support_share_title": "Share your support",
            "support_share_desc": "No online payment — leave your details and we will contact you soon.",
            "support_thanks_msg": "Thank you. We received your commitment and will contact you soon.",
            "support_form_name": "Name",
            "support_form_phone": "Phone number",
            "support_form_commitment": "Total commitment",
            "support_form_referral": "Referred by",
            "support_form_optional": "optional",
            "support_referral_placeholder": "AHC member referral code",
            "support_referral_hint": "If a classmate invited you, enter their code (e.g. name2017). We check that the code exists.",
            "support_referral_valid": "Valid referral code.",
            "support_referral_not_found": "Referral code not found.",
            "support_referral_try_blank": "Check the code or leave it blank.",
            "support_submit": "Submit",
            "status_pending_payment": "Pending Payment",
            "status_pending": "Pending",
            "status_paid": "Paid",
            "status_ready": "Ready",
            "status_processing": "Processing",
            "status_shipped": "Shipped",
            "status_completed": "Completed",
            "status_cancelled": "Cancelled",
            "status_preorder": "Preorder",
            "track_not_shipped": "Not shipped yet",
            "track_confirmed_after": "Confirmed after order",
            "track_step_placed": "Order placed",
            "track_step_payment": "Payment confirmed",
            "track_step_preparing": "Preparing merchandise",
            "track_step_shipped": "Shipped",
            "track_step_completed": "Completed"
        },
        "id": {
            "explore": "Jelajahi FRACO",
            "shop": "Belanja Merchandise",
            "about_title": "Tentang FRACO",
            "learn_more": "Selengkapnya",
            "programs_title": "Program Kami",
            "view_all": "Lihat Semua",
            "merch_title": "Merchandise",
            "shop_all": "Belanja Semua Merchandise",
            "add_cart": "Tambah ke Keranjang",
            "view": "Lihat",
            "partners_title": "Mitra",
            "partners_kicker": "Bangun bersama kami",
            "partners_heading": "Mari Bangun bersama FRACO",
            "partners_body": "Perusahaan, merek, bisnis, dan organisasi dapat berkolaborasi dengan FRACO — angkatan 2017 — pada {event} melalui sponsorship, layanan vendor, dan booth universitas.",
            "become_sponsor": "Jadi Sponsor",
            "download_proposal": "Unduh Proposal",
            "updates_title": "Update Terbaru",
            "gallery_title": "Galeri",
            "nav_home": "Beranda",
            "nav_about": "Tentang",
            "nav_support": "Dukung Kami",
            "nav_cart": "Keranjang",
            "nav_help": "Bantuan",
            "nav_login": "Login",
            "nav_account": "Akun",
            "footer_navigate": "Navigasi",
            "footer_participate": "Ikut Serta",
            "footer_contact": "Kontak",
            "search_placeholder": "Cari program, merch, dan update FRACO...",
            "search_btn": "Cari",
            "search_close": "Tutup",
            "about_h1": "Tentang",
            "about_community": "Komunitas",
            "about_fraco_heading": "Tentang FRACO",
            "about_ahc_heading": "Tentang Alumni Home Coming",
            "about_activities_title": "Kegiatan utama",
            "about_view_programs": "Lihat Program",
            "about_timeline_title": "Linimasa",
            "about_timeline_range": "Agustus 2026 — April 2027",
            "about_timeline_empty": "Linimasa akan muncul di sini seiring tanggal persiapan dikonfirmasi.",
            "about_team_title": "Tim Kami",
            "about_divisions_label": "Divisi FRACO",
            "about_division": "Divisi",
            "about_divisions_empty": "Daftar divisi akan muncul di sini.",
            "about_register": "Daftar",
            "about_explore_programs": "Jelajahi Program",
            "shop_h1": "Belanja",
            "proof_supporting": "Sudah mendukung FRACO",
            "proof_customers": "pelanggan telah membeli merchandise",
            "proof_merch_total": "Total merchandise terbeli",
            "proof_paid_orders": "pesanan terbayar",
            "badge_in_stock": "Tersedia",
            "badge_out_stock": "Stok habis",
            "badge_preorder": "Preorder",
            "size_kids": "Anak",
            "size_guide_title": "Panduan ukuran",
            "size_lebar": "Lebar",
            "size_panjang": "Panjang",
            "size_note": "Ukuran dalam cm · toleransi +/-2-3 cm",
            "cart_title": "Keranjang",
            "cart_continue": "Lanjut belanja",
            "cart_qty": "Jml",
            "cart_remove": "Hapus",
            "cart_subtotal": "Subtotal",
            "cart_shipping": "Pengiriman",
            "cart_total": "Total",
            "cart_preorder_note": "Termasuk item preorder · perkiraan {eta}. Pembayaran tetap mengonfirmasi pesanan.",
            "cart_ready_eta": "Siap {eta}",
            "cart_checkout": "Checkout",
            "cart_empty": "Keranjang Anda masih kosong.",
            "stamp_paid": "LUNAS",
            "badge_in_stock_cap": "Tersedia",
            "badge_out_stock_cap": "Stok Habis",
            "size_one": "Satu Ukuran",
            "merch_all_products": "Semua Produk",
            "support_anonymous": "Anonim",
            "support_fallback_name": "Pendukung FRACO",
            "support_amount_fallback": "Dukungan",
            "merch_preorder_open": "Stok habis · preorder dibuka",
            "merch_ready_ship": "Siap kirim",
            "merch_unavailable": "Tidak tersedia",
            "merch_see_product": "Lihat produk",
            "merch_empty_category": "Belum ada produk di kategori ini.",
            "search_label": "Pencarian:",
            "track_kicker": "Pelacakan pesanan",
            "track_title": "Lacak merchandise Anda",
            "track_desc": "Masukkan kode transaksi yang muncul setelah checkout untuk melihat progres pembayaran, pengiriman, dan merchandise.",
            "track_code_label": "Kode transaksi",
            "track_code_placeholder": "Contoh: FR1788508509",
            "track_btn": "Lacak pesanan",
            "track_not_found": "Tidak ditemukan pesanan merchandise untuk {code}. Periksa kode dan coba lagi.",
            "track_general": "Informasi umum",
            "track_total": "Total:",
            "track_payment": "Status pembayaran",
            "track_order": "Pesanan:",
            "track_shipping": "Status pengiriman",
            "track_expedition": "Ekspedisi:",
            "track_code": "Kode resi:",
            "track_shipment": "Lacak kiriman →",
            "track_cancelled": "Pesanan ini dibatalkan.",
            "track_progress": "Progres merchandise",
            "track_items": "Item",
            "track_preorder_note": "Termasuk merchandise preorder · perkiraan {eta}.",
            "support_proof_supporters": "pendukung telah berkontribusi",
            "support_proof_total": "Total dukungan diterima",
            "support_thanks_line": "Terima kasih telah menjaga {event} terus berjalan",
            "support_top_title": "Pendukung teratas",
            "support_top_desc": "Terima kasih — teman, keluarga, dan teman seangkatan {year} yang menjaga {event} tetap berjalan.",
            "support_donor_label": "Dukungan",
            "support_donors_empty": "Pendukung akan segera muncul di sini.",
            "support_contact_email": "Email",
            "support_contact_whatsapp": "WhatsApp",
            "support_contact_phone": "Telepon",
            "support_chat_whatsapp": "Chat via WhatsApp",
            "support_whatsapp_us": "Hubungi via WhatsApp",
            "support_email_us": "Kirim email",
            "support_share_title": "Bagikan dukungan Anda",
            "support_share_desc": "Tidak ada pembayaran online — tinggalkan data Anda dan kami akan segera menghubungi.",
            "support_thanks_msg": "Terima kasih. Komitmen Anda sudah kami terima dan kami akan segera menghubungi.",
            "support_form_name": "Nama",
            "support_form_phone": "Nomor telepon",
            "support_form_commitment": "Total komitmen",
            "support_form_referral": "Dirujuk oleh",
            "support_form_optional": "opsional",
            "support_referral_placeholder": "Kode referral anggota AHC",
            "support_referral_hint": "Jika teman seangkatan mengundang Anda, masukkan kodenya (cth. nama2017). Kami memeriksa bahwa kode tersebut ada.",
            "support_referral_valid": "Kode referral valid.",
            "support_referral_not_found": "Kode referral tidak ditemukan.",
            "support_referral_try_blank": "Periksa kodenya atau biarkan kosong.",
            "support_submit": "Kirim",
            "status_pending_payment": "Menunggu Pembayaran",
            "status_pending": "Menunggu",
            "status_paid": "Dibayar",
            "status_ready": "Siap",
            "status_processing": "Diproses",
            "status_shipped": "Dikirim",
            "status_completed": "Selesai",
            "status_cancelled": "Dibatalkan",
            "status_preorder": "Preorder",
            "track_not_shipped": "Belum dikirim",
            "track_confirmed_after": "Dikonfirmasi setelah pesanan",
            "track_step_placed": "Pesanan dibuat",
            "track_step_payment": "Pembayaran dikonfirmasi",
            "track_step_preparing": "Menyiapkan merchandise",
            "track_step_shipped": "Dikirim",
            "track_step_completed": "Selesai"
        }
    }

    def __init__(self, app=None):
        self.webapp = app
        seeder = ahc_site_seed(app)
        seeder.seed_if_empty()
    # end def

    def get_lang(self):
        lang = "id"
        try:
            from flask import has_request_context, request, session
            if not has_request_context():
                return "id"
            # end if
            q = (request.args.get("lang") or "").strip().lower()
            if q in ["en", "id"]:
                return q
            # end if
            cookie = (request.cookies.get("fraco_lang") or "").strip().lower()
            if cookie in ["en", "id"]:
                return cookie
            # end if
            sess = (session.get("fraco_lang") or "").strip().lower()
            if sess in ["en", "id"]:
                return sess
            # end if
        except Exception:
            lang = "id"
        # end try
        return lang
    # end def

    def get_site(self):
        rec = self.mgdDB.db_site.find_one({"is_deleted": False}, {"_id": 0})
        if rec == None:
            return {}
        # end if
        return rec
    # end def

    def shipping_minimum_num(self, site=None):
        row = site if site != None else self.get_site()
        row = row or {}
        value = row.get("shipping_minimum_progress_num")
        if value == None:
            return 100000
        # end if
        minimum = int(value)
        if minimum < 0:
            minimum = 0
        # end if
        return minimum
    # end def

    def apply_lang(self, site, lang="en"):
        data = dict(site or {})
        if lang == "id":
            for key in self.LANG_FIELDS:
                alt = (data.get(key + "_id") or "").strip()
                if alt != "":
                    data[key] = alt
                # end if
            # end for
        # end if
        data["lang"] = lang
        ui = dict(self.UI.get(lang) or self.UI["en"])
        event = (data.get("event_full_name") or "Alumni Home Coming 2027").strip()
        ui["partners_body"] = ui["partners_body"].replace("{event}", event)
        data["ui"] = ui
        return data
    # end def

    def get_auth_user(self):
        user = None
        try:
            from flask import has_request_context, session
            if not has_request_context():
                return None
            # end if
            pkey = session.get("auth_pkey", "")
            if pkey == "":
                return None
            # end if
            user = self.mgdDB.db_user.find_one(
                {"pkey": pkey, "is_deleted": False, "status": "ENABLE"},
                {"_id": 0, "password": 0}
            )
        except Exception:
            user = None
        # end try
        return user
    # end def

    def abs_public_url(self, path):
        base = (config.G_PUBLIC_SITE_URL or "").strip().rstrip("/")
        text = str(path or "").strip()
        if text == "":
            text = "/"
        # end if
        if text.lower().find("http://") == 0 or text.lower().find("https://") == 0:
            return text
        # end if
        if base == "":
            try:
                from flask import has_request_context, request
                if has_request_context():
                    base = (request.url_root or "").strip().rstrip("/")
                # end if
            except Exception:
                base = ""
            # end try
        # end if
        if not text.startswith("/"):
            text = "/" + text
        # end if
        if base == "":
            return text
        # end if
        return base + text
    # end def

    def default_share_meta(self, site, lang="en"):
        name = (site.get("name") or "FRACO").strip()
        event = (site.get("event_full_name") or "Alumni Home Coming 2027").strip()
        class_label = (site.get("class_label") or "Class of 2017").strip()
        share_title = name + " | " + class_label + " | " + event
        desc = (site.get("subtitle") or site.get("description") or "").strip()
        if desc == "":
            if lang == "id":
                desc = (
                    "FRACO angkatan 2017 — program, merchandise, mitra, dan Support Us untuk "
                    + event + "."
                )
            else:
                desc = (
                    "FRACO · " + class_label + " — programs, merchandise, partners, "
                    + "and Support Us for " + event + "."
                )
            # end if
        # end if
        return {
            "share_title": share_title,
            "share_description": desc,
            "share_url": "/",
            "share_image": config.G_OG_IMAGE_PATH
        }
    # end def

    def with_site(self, extra):
        site = self.get_site()
        lang = self.get_lang()
        data = self.apply_lang(site, lang)
        data["cart_count"] = self.get_cart_count()
        data["auth_user"] = self.get_auth_user()
        data.update(extra or {})
        lang = data.get("lang") or lang
        share = self.default_share_meta(self.apply_lang(site, lang), lang)
        for key in ["share_title", "share_description", "share_url", "share_image"]:
            val = data.get(key)
            if val != None and str(val).strip() != "":
                share[key] = val
            # end if
        # end for
        share["share_url"] = self.abs_public_url(share.get("share_url") or "/")
        share["share_image"] = self.abs_public_url(share.get("share_image") or config.G_OG_IMAGE_PATH)
        share["share_description"] = (share.get("share_description") or "").strip()
        if len(share["share_description"]) > 300:
            share["share_description"] = share["share_description"][0:297] + "..."
        # end if
        data.update(share)
        return data
    # end def

    def get_cart_count(self):
        total = 0
        try:
            from flask import has_request_context, session
            if not has_request_context():
                return 0
            # end if
            sid = session.get("cart_sid", "")
            if sid == "":
                return 0
            # end if
            rows = self.mgdDB.db_cart.find(
                {"session_id": sid, "is_deleted": False},
                {"qty": 1}
            )
            for row in rows:
                total = total + int(row.get("qty", 0))
            # end for
        except Exception:
            total = 0
        # end try
        return total
    # end def
# end class
