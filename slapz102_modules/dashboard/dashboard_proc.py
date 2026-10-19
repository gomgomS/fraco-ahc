import sys
import re
import uuid

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import has_request_context, session
from werkzeug.security import generate_password_hash, check_password_hash
from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
from address.address_proc import address_proc

class dashboard_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    NAV_KEYS = [
        ("overview", "/dashboard"),
        ("orders", "/dashboard/orders"),
        ("proposal", "/dashboard/proposal"),
        ("events", "/dashboard/events"),
        ("profile", "/dashboard/profile")
    ]
    NAV_ALUMNI_KEYS = [
        ("overview", "/dashboard"),
        ("events", "/dashboard/events"),
        ("profile", "/dashboard/profile")
    ]
    ORDER_STATUSES = [
        "Pending Payment", "Preorder", "Paid", "Ready", "Processing", "Shipped", "Completed", "Cancelled"
    ]
    ORDER_PAY_STATUSES = ["Pending", "Paid"]
    SHIPPING_HANDLERS = ["OFFICER", "SELF"]

    DASH = {
        "en": {
            "nav_overview": "Overview",
            "nav_orders": "My Merchandise Orders",
            "nav_proposal": "My Proposal",
            "nav_events": "Events",
            "nav_profile": "Profile",
            "logout": "Log out",
            "hello": "Hello, {name}",
            "opening": "Opening",
            "opening_message": (
                "Hi teammates — as Alumni Home Coming 2017 draws nearer, we need real support and funding. "
                "That is why it matters that every classmate stays active in raising funds through this work: "
                "share your referral, help sell merchandise, and bring supporters in through Support Us. "
                "Together we can carry AHC all the way."
            ),
            "your_referral": "Your referral",
            "merch_profit": "Merch profit",
            "referral_orders": "Referral orders",
            "support_pledges": "Support pledges",
            "alumni_welcome": "Welcome to your FRACO account. Browse events and keep your profile up to date.",
            "orders_title": "My Merchandise Orders",
            "orders_intro": "Referral checkouts you fulfill with your code. Update location and status as you pack.",
            "referral_code": "Referral code",
            "shared_target": "Shared member target",
            "raised_total": "Raised total",
            "left_to_target": "Left to target",
            "achieved": "Achieved",
            "progress": "Progress",
            "proposal_label": "Proposal",
            "own_contribution": "Own contribution",
            "paid_orders": "Paid orders",
            "unpaid_leads": "Unpaid leads",
            "not_counted_yet": "not counted yet",
            "above_target": "Above target by",
            "unpaid_title": "Unpaid leads — follow up",
            "unpaid_intro": "These buyers used your referral but have not paid yet. Their profit does not count toward your shared target until payment is Paid.",
            "potential_profit": "Potential profit",
            "show_pending": "Show pending payment orders",
            "orders_rule": "Profit = sale − bahan baku. Only Paid orders accumulate to your shared target. Pending / failed / refunded / cancelled do not.",
            "filter_order_line": "Order / line",
            "filter_payment": "Payment",
            "all": "All",
            "counts_target": "Counts to target",
            "not_counted": "Not counted yet",
            "unpaid_card_hint": "{name} wants to buy, but payment is still {pay}. Follow up — this profit will only count once Paid.",
            "lead_message": "{name} wants to buy through your referral, but payment is still {pay}. Follow up so this can count toward your shared target.",
            "buyer_contact": "Buyer contact",
            "search_contact": "Search buyer contact",
            "search_contact_placeholder": "Name, email, or phone",
            "search_btn": "Search",
            "clear_search": "Clear",
            "view_only": "view only",
            "delivery_location": "Delivery location",
            "change_location": "Change location",
            "cancel": "Cancel",
            "address": "Address",
            "street": "Street, building, house no.",
            "address_detail": "Other details",
            "province": "Province",
            "district": "District",
            "village": "Village / kelurahan",
            "city": "City / regency",
            "postal_code": "Postal code",
            "location_hint": "Choose the Indonesian region, then save. Postal code fills automatically.",
            "edit_on_detail": "Edit full address on the order page",
            "items_label": "Items",
            "status_per_size": "status per size",
            "line_status": "Line status",
            "order_controls": "Order controls",
            "payment_status": "Payment status",
            "set_all_lines": "Set all lines to",
            "set_all_hint": "Updates every size / line and the main order status. Changing one line alone does not change the main status.",
            "order_status": "Order status",
            "save_changes": "Save changes",
            "order_updated": "Order updated.",
            "no_match": "No referral orders match",
            "show_all": "Show all",
            "no_orders": "No referral orders yet. Share code {code} at checkout.",
            "orders_ahc_only": "This page is for AHC members who sell with a referral code.",
            "proposal_title": "My Proposal",
            "proposal_intro": "Proposal: track Support Us pledges that used your code, plus your own contributions, against the shared member target.",
            "events_title": "Events",
            "events_intro": "Events in your account: see dated activities and whether you can still register.",
            "events_empty": "Public event days will appear here when FRACO locks them.",
            "profile_title": "Profile",
            "profile_saved": "Profile saved.",
            "full_name": "Full name",
            "username_email": "Username / email",
            "phone": "Phone",
            "optional": "optional",
            "save_profile": "Save profile",
            "name": "Name",
            "email": "Email",
            "sale": "Sale",
            "bahan_baku": "Bahan baku",
            "your_profit": "Your profit",
            "proposal_received": "Proposal received",
            "pending_follow_up": "Pending follow-up",
            "self_pending_note": "Your pending own contribution: {amount} (counts after FRACO marks Received).",
            "above_target_thanks": "Above target by {amount} — thank you.",
            "add_own_title": "Add your own contribution",
            "add_own_intro": "Pledge an amount yourself. It stays under Follow up until FRACO marks it Received — then it appears as your Contribution.",
            "pledge_saved": "Pledge saved. It will appear under Follow up until confirmed.",
            "commitment_amount": "Commitment amount",
            "commitment_placeholder": "e.g. 500000 or Rp 500.000",
            "submit_pledge": "Submit pledge",
            "tab_follow_up": "Follow up",
            "tab_done": "Done",
            "th_name": "Name",
            "th_phone": "Phone",
            "th_commitment": "Commitment",
            "th_date": "Date",
            "no_received_pledges": "No received pledges yet.",
            "nothing_follow_up": "Nothing waiting for follow-up.",
            "no_pledges_yet": "No support pledges yet. Share your code on Support Us, or add your own contribution above.",
            "profile_share_hint": "Shared on merchandise checkout and Support Us.",
            "waiting_stock": "Waiting for stock",
            "stock_ready": "Stock ready — move to Processing / Shipped when you pack and send.",
            "started_preorder": "Started as preorder",
            "editable": "editable",
            "delivery_updated": "Delivery location updated.",
            "save_delivery": "Save delivery location",
            "shipping_arrangement": "Shipping arrangement",
            "tab_order_details": "Order details",
            "tab_shipping": "Shipping",
            "view_transaction_details": "View transaction details →",
            "shipping_saved": "Shipping choice saved.",
            "shipping_available": "Available combined progress",
            "shipping_minimum_copy": "Officer shipping requires at least {minimum} before requesting it.",
            "shipping_contribute_first": "Please contribute first.",
            "shipping_notice_title": "Important:",
            "shipping_notice": "Shipping costs plus the wrapping, packing, and arrangement service fee will be deducted from your earnings and combined target progress.",
            "shipping_handler_label": "Who will arrange shipping?",
            "shipping_select_type": "Select shipping type",
            "shipping_by_officer": "FRACO officer handles shipping",
            "shipping_by_self": "I arrange shipping myself",
            "shipping_same_buyer": "Package recipient and address are the same as the buyer",
            "shipping_package_recipient": "Package recipient",
            "shipping_package_address": "Package address",
            "shipping_recipient_name": "Package recipient name",
            "shipping_recipient_phone": "Package recipient phone",
            "shipping_package_note": "Note printed / written on the package",
            "shipping_confirm_info": "I confirm the recipient contact and address are correct. This information will be written on the package; incorrect information is not the responsibility of FRACO officers or staff.",
            "shipping_confirm_process": "I understand that after saving, the order enters the shipping process and this request cannot be cancelled.",
            "shipping_officer_status": "Officer shipping status",
            "shipping_expense": "Shipping expense",
            "shipping_service_fee": "Wrapping, packing, and arrangement service",
            "shipping_total_deduction": "Total shipping deduction",
            "shipping_per_order": "per order",
            "shipping_cost_deduction": "Shipping cost deduction",
            "shipping_cost_deducted": "This cost has been deducted from your earnings and combined target progress.",
            "shipping_cost_scheduled": "These amounts are saved on this order. They fully count against your combined progress once officer shipping status is Processing or later.",
            "shipping_deducted_copy": "Officer shipping expense deducted from combined progress",
            "shipping_tracking_code": "Tracking code",
            "shipping_track": "Track shipment →",
            "shipping_save": "Save shipping choice",
            "shipping_select_error": "Select who will arrange shipping",
            "shipping_cancel_locked": "The officer shipping request has been submitted and cannot be cancelled. Contact an admin if something needs correcting.",
            "shipping_minimum_error": "Officer shipping requires at least {minimum} combined progress. Please contribute first.",
            "shipping_confirm_error": "Confirm that the package information is correct",
            "shipping_process_confirm_error": "Confirm that you understand the shipping request cannot be cancelled",
            "shipping_address_locked": "The delivery address is locked because shipping is handled by a FRACO officer.",
            "shipping_member_edits_locked": "Order details are locked while shipping is handled by a FRACO officer.",
            "shipping_wait_shipped": "The officer is handling this shipment. You can complete the order after its shipping status is SHIPPED.",
            "shipping_complete_order": "Complete order",
            "shipping_complete_confirm": "Confirm that you have received this order?",
            "shipping_completed": "Order completed.",
            "shipping_status_requested": "Waiting for officer",
            "shipping_status_processing": "Being processed",
            "shipping_status_shipped": "Shipped",
            "shipping_status_completed": "Completed",
            "shipping_status_self": "Self-arranged",
            "shipping_status_empty": "Not selected",
            "status_pending_payment": "Pending payment",
            "status_preorder": "Preorder",
            "status_paid": "Paid",
            "status_ready": "Ready",
            "status_processing": "Processing",
            "status_shipped": "Shipped",
            "status_completed": "Completed",
            "status_cancelled": "Cancelled",
            "status_pending": "Pending",
            "shipping_recipient_error": "Package recipient name, phone, and address are required",
            "transaction_information": "Transaction information",
            "transaction_code": "Transaction code",
            "account": "Account",
            "not_assigned": "Not assigned",
            "order_total": "Order total",
            "subtotal": "Subtotal",
            "discount": "Discount",
            "shipping": "Shipping",
            "total": "Total",
            "notes": "Notes",
            "qty": "Qty",
            "each": "each",
            "merch_progress_msg": (
                "One class target for each member: {target}. "
                "Merchandise profit counts only after payment is Paid. "
                "Support Us referrals and your own contribution also count toward the same target."
            ),
            "proposal_progress_msg": (
                "One class target for each member: {target}. "
                "Merchandise profit counts only after payment is Paid. "
                "Support Us referrals and your own contribution also count toward the same target."
            )
        },
        "id": {
            "nav_overview": "Beranda",
            "nav_orders": "Pesanan Merch",
            "nav_proposal": "Proposal",
            "nav_events": "Acara",
            "nav_profile": "Profil",
            "logout": "Keluar",
            "hello": "Hai, {name}!",
            "opening": "Kata pembuka",
            "opening_message": (
                "Hai semuanya — AHC makin dekat, kita butuh dukungan yang nyata. "
                "Yuk aktif bareng: bagikan kode referral, bantu jual merch, "
                "dan ajak orang ikut Support Us. Kalau kompak, AHC pasti jalan."
            ),
            "your_referral": "Kode referral kamu",
            "merch_profit": "Profit merch",
            "referral_orders": "Pesanan dari referral",
            "support_pledges": "Dukungan Support Us",
            "alumni_welcome": "Selamat datang di akun FRACO kamu. Bisa cek acara dan update profil di sini.",
            "orders_title": "Pesanan Merch",
            "orders_intro": "Ini daftar orang yang checkout pakai kode kamu. Update lokasi & status pas lagi packing ya.",
            "referral_code": "Kode referral",
            "shared_target": "Target bareng kelas",
            "raised_total": "Sudah terkumpul",
            "left_to_target": "Masih kurang",
            "achieved": "Sudah tembus!",
            "progress": "Progres",
            "proposal_label": "Proposal",
            "own_contribution": "Kontribusi sendiri",
            "paid_orders": "Sudah bayar",
            "unpaid_leads": "Belum bayar",
            "not_counted_yet": "belum masuk hitungan",
            "above_target": "Kelebihan target",
            "unpaid_title": "Masih ada yang belum bayar — yuk chat",
            "unpaid_intro": "Mereka udah checkout pakai kode kamu, tapi belum bayar. Profit-nya baru masuk target setelah statusnya Paid.",
            "potential_profit": "Potensi profit",
            "show_pending": "Lihat yang masih pending",
            "orders_rule": "Profit = harga jual − bahan baku. Yang masuk target cuma yang sudah Paid. Pending, gagal, refund, atau batal? Belum dihitung.",
            "filter_order_line": "Status barang",
            "filter_payment": "Status bayar",
            "all": "Semua",
            "counts_target": "Masuk target",
            "not_counted": "Belum masuk",
            "unpaid_card_hint": "{name} mau beli, tapi pembayarannya masih {pay}. Yuk follow up — baru dihitung setelah Paid.",
            "lead_message": "{name} mau beli lewat kode kamu, tapi pembayarannya masih {pay}. Chat dulu biar bisa masuk target bareng.",
            "buyer_contact": "Kontak pembeli",
            "search_contact": "Cari kontak pembeli",
            "search_contact_placeholder": "Nama, email, atau no. HP",
            "search_btn": "Cari",
            "clear_search": "Hapus",
            "view_only": "cuma lihat",
            "delivery_location": "Alamat kirim",
            "change_location": "Ubah alamat",
            "cancel": "Batal",
            "address": "Alamat",
            "street": "Nama jalan, gedung, no. rumah",
            "address_detail": "Detail lainnya",
            "province": "Provinsi",
            "district": "Kecamatan",
            "village": "Kelurahan / desa",
            "city": "Kabupaten / kota",
            "postal_code": "Kode pos",
            "location_hint": "Pilih wilayah Indonesia, lalu simpan. Kode pos terisi otomatis.",
            "edit_on_detail": "Ubah alamat lengkap di halaman pesanan",
            "items_label": "Barang",
            "status_per_size": "status per ukuran",
            "line_status": "Status ukuran",
            "order_controls": "Atur pesanan",
            "payment_status": "Status bayar",
            "set_all_lines": "Samakan semua ke",
            "set_all_hint": "Ini ngubah semua ukuran sekaligus + status utama. Kalau cuma satu ukuran yang diubah, status utama tetap.",
            "order_status": "Status pesanan",
            "save_changes": "Simpan",
            "order_updated": "Berhasil disimpan.",
            "no_match": "Nggak ada pesanan yang cocok",
            "show_all": "Lihat semua",
            "no_orders": "Belum ada pesanan. Bagikan kode {code} pas orang checkout ya.",
            "orders_ahc_only": "Halaman ini buat anggota AHC yang jual pakai kode referral.",
            "proposal_title": "Proposal",
            "proposal_intro": "Pantau dukungan Support Us yang pakai kode kamu, plus kontribusi sendiri, menuju target bareng kelas.",
            "events_title": "Acara",
            "events_intro": "Lihat jadwal acara dan apakah masih bisa daftar.",
            "events_empty": "Jadwal acara publik belum keluar. Nanti muncul di sini.",
            "profile_title": "Profil",
            "profile_saved": "Profil berhasil disimpan.",
            "full_name": "Nama lengkap",
            "username_email": "Username / email",
            "phone": "No. HP",
            "optional": "boleh dikosongin",
            "save_profile": "Simpan profil",
            "name": "Nama",
            "email": "Email",
            "sale": "Penjualan",
            "bahan_baku": "Bahan baku",
            "your_profit": "Profit kamu",
            "proposal_received": "Dari proposal",
            "pending_follow_up": "Masih follow up",
            "self_pending_note": "Kontribusi sendiri yang masih pending: {amount} (baru dihitung setelah FRACO tandai Received).",
            "above_target_thanks": "Kelebihan target {amount} — makasih banyak!",
            "add_own_title": "Tambah kontribusi sendiri",
            "add_own_intro": "Mau ikut iuran sendiri? Isi nominal di sini. Statusnya Follow up dulu sampai FRACO tandai Received — baru muncul sebagai Kontribusi kamu.",
            "pledge_saved": "Berhasil disimpan. Masih di Follow up sampai dikonfirmasi FRACO.",
            "commitment_amount": "Nominal komitmen",
            "commitment_placeholder": "contoh: 500000 atau Rp 500.000",
            "submit_pledge": "Kirim",
            "tab_follow_up": "Follow up",
            "tab_done": "Selesai",
            "th_name": "Nama",
            "th_phone": "HP",
            "th_commitment": "Nominal",
            "th_date": "Tanggal",
            "no_received_pledges": "Belum ada yang sudah diterima.",
            "nothing_follow_up": "Belum ada yang nunggu follow up.",
            "no_pledges_yet": "Belum ada dukungan. Bagikan kode kamu di Support Us, atau isi kontribusi sendiri di atas.",
            "profile_share_hint": "Dipakai di checkout merch dan Support Us.",
            "waiting_stock": "Masih nunggu stok",
            "stock_ready": "Stok siap — ubah ke Processing / Shipped pas packing & kirim.",
            "started_preorder": "Awalnya preorder",
            "editable": "bisa diubah",
            "delivery_updated": "Alamat pengiriman berhasil diperbarui.",
            "save_delivery": "Simpan alamat",
            "shipping_arrangement": "Pengiriman barang",
            "tab_order_details": "Detail pesanan",
            "tab_shipping": "Pengiriman",
            "view_transaction_details": "Lihat detail transaksi →",
            "shipping_saved": "Pilihan pengiriman berhasil disimpan.",
            "shipping_available": "Progress gabungan yang bisa dipakai",
            "shipping_minimum_copy": "Kalau mau dibantu tim FRACO, progress gabunganmu minimal {minimum}.",
            "shipping_contribute_first": "Yuk kontribusi dulu.",
            "shipping_notice_title": "Perlu kamu tahu:",
            "shipping_notice": "Kalau pengiriman diurus tim FRACO, ongkir serta biaya layanan pembungkusan, packing, dan pengaturan pengiriman akan dipotong dari penghasilan dan progress target gabunganmu.",
            "shipping_handler_label": "Siapa yang akan urus pengirimannya?",
            "shipping_select_type": "Pilih cara pengiriman",
            "shipping_by_officer": "Tim FRACO yang urus pengiriman",
            "shipping_by_self": "Saya urus pengiriman sendiri",
            "shipping_same_buyer": "Penerima paket dan alamatnya sama seperti data pembeli",
            "shipping_package_recipient": "Penerima paket",
            "shipping_package_address": "Alamat paket",
            "shipping_recipient_name": "Nama penerima paket",
            "shipping_recipient_phone": "Nomor HP penerima paket",
            "shipping_package_note": "Catatan yang mau ditulis di paket",
            "shipping_confirm_info": "Saya sudah cek dan memastikan kontak serta alamat penerima benar. Data ini akan ditulis di paket; kalau datanya salah, itu bukan tanggung jawab officer atau staf FRACO.",
            "shipping_confirm_process": "Saya paham setelah disimpan, pesanan akan masuk proses pengiriman dan permintaan ini tidak bisa dibatalkan.",
            "shipping_officer_status": "Status pengiriman oleh tim FRACO",
            "shipping_expense": "Biaya pengiriman",
            "shipping_service_fee": "Layanan pembungkusan, packing, dan pengaturan pengiriman",
            "shipping_total_deduction": "Total potongan pengiriman",
            "shipping_per_order": "per pesanan",
            "shipping_cost_deduction": "Potongan biaya pengiriman",
            "shipping_cost_deducted": "Biaya ini sudah dipotong dari penghasilan dan progress target gabunganmu.",
            "shipping_cost_scheduled": "Nominal ini sudah tercatat di pesanan. Akan dipotong penuh dari progress gabungan setelah status pengiriman officer Processing atau setelahnya.",
            "shipping_deducted_copy": "Biaya pengiriman oleh tim FRACO yang dipotong dari progress gabungan",
            "shipping_tracking_code": "Nomor resi",
            "shipping_track": "Lacak paket →",
            "shipping_save": "Simpan pilihan pengiriman",
            "shipping_select_error": "Pilih dulu siapa yang akan urus pengiriman",
            "shipping_cancel_locked": "Permintaan pengiriman ke tim FRACO sudah dikirim dan tidak bisa dibatalkan. Hubungi admin kalau ada data yang perlu diperbaiki.",
            "shipping_minimum_error": "Untuk dibantu tim FRACO, progress gabunganmu minimal {minimum}. Yuk kontribusi dulu.",
            "shipping_confirm_error": "Centang konfirmasi bahwa data paketnya sudah benar",
            "shipping_process_confirm_error": "Centang konfirmasi bahwa permintaan pengiriman tidak bisa dibatalkan",
            "shipping_address_locked": "Alamat pengiriman sudah dikunci karena pengiriman diurus oleh tim FRACO.",
            "shipping_member_edits_locked": "Detail pesanan sudah dikunci selama pengiriman diurus oleh tim FRACO.",
            "shipping_wait_shipped": "Pengiriman sedang diurus tim FRACO. Kamu bisa menyelesaikan pesanan setelah status pengiriman menjadi SHIPPED.",
            "shipping_complete_order": "Pesanan sudah diterima",
            "shipping_complete_confirm": "Yakin pesanan ini sudah kamu terima?",
            "shipping_completed": "Pesanan berhasil diselesaikan.",
            "shipping_status_requested": "Menunggu diproses tim FRACO",
            "shipping_status_processing": "Sedang diproses",
            "shipping_status_shipped": "Sudah dikirim",
            "shipping_status_completed": "Selesai",
            "shipping_status_self": "Dikirim sendiri",
            "shipping_status_empty": "Belum dipilih",
            "status_pending_payment": "Menunggu pembayaran",
            "status_preorder": "Preorder",
            "status_paid": "Sudah dibayar",
            "status_ready": "Siap diproses",
            "status_processing": "Sedang diproses",
            "status_shipped": "Sudah dikirim",
            "status_completed": "Selesai",
            "status_cancelled": "Dibatalkan",
            "status_pending": "Menunggu pembayaran",
            "shipping_recipient_error": "Nama, nomor HP, dan alamat penerima paket wajib diisi",
            "transaction_information": "Informasi transaksi",
            "transaction_code": "Kode transaksi",
            "account": "Akun penerima",
            "not_assigned": "Belum ditentukan",
            "order_total": "Total pesanan",
            "subtotal": "Subtotal",
            "discount": "Diskon",
            "shipping": "Ongkir",
            "total": "Total",
            "notes": "Catatan",
            "qty": "Jumlah",
            "each": "per item",
            "merch_progress_msg": (
                "Seperti yang kita tahu, hasil keputusan kelas target kita {target}. "
                "Tenang aja temen-temen — bisa ngejar lewat kirim proposal, ajak dukungan Support Us, jual merch pakai kode referral, "
                "atau ikut kontribusi sendiri. Profit merch baru dihitung kalau sudah Paid. Yuk bareng-bareng tembus target!"
            ),
            "proposal_progress_msg": (
                "Seperti yang kita tahu, hasil keputusan kelas target kita {target}. "
                "Jangan khawatir — kirim proposal, ajak orang Support Us, jual merch, atau ikut iuran sendiri. "
                "Yang penting kompak. Yuk kita kejar bareng!"
            )
        }
    }

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
        self.address = address_proc(app)
    # end def

    def dash_copy(self):
        lang = self.site.get_lang()
        return dict(self.DASH.get(lang) or self.DASH["en"])
    # end def

    def dash_nav(self, is_ahc=True):
        copy = self.dash_copy()
        keys = self.NAV_KEYS if is_ahc else self.NAV_ALUMNI_KEYS
        rows = []
        for key, href in keys:
            label = copy.get("nav_" + key) or key
            rows.append((key, href, label))
        # end for
        return rows
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return "Rp 0"
        # end if
        text = "{:,}".format(n).replace(",", ".")
        return "Rp " + text
    # end def

    def current_user(self):
        return self.site.get_auth_user()
    # end def

    def login_user(self, pkey):
        session["auth_pkey"] = pkey
        if session.get("cart_sid", "") == "":
            session["cart_sid"] = str(uuid.uuid4())
        # end if
        self.link_rows(pkey)
    # end def

    def logout_user(self):
        session.pop("auth_pkey", None)
    # end def

    def link_rows(self, pkey):
        user = self.mgdDB.db_user.find_one({"pkey": pkey, "is_deleted": False}, {"_id": 0})
        if user == None:
            return
        # end if
        email = (user.get("email") or "").lower()
        if email == "":
            return
        # end if
        self.mgdDB.db_participant.update_many(
            {"email": email, "is_deleted": False},
            {"$set": {"fk_user_id": pkey}}
        )
        self.mgdDB.db_order.update_many(
            {"email": email, "is_deleted": False},
            {"$set": {"fk_user_id": pkey}}
        )
    # end def

    def login(self, params, raw_password):
        response = {"status": "FAILED", "desc": ""}
        email = (params.get("email") or "").strip().lower()
        phone = (params.get("phone") or "").strip()
        if email == "" or raw_password == "":
            response["desc"] = "Username / email and password are required"
            return response
        # end if
        user = self.mgdDB.db_user.find_one({
            "is_deleted": False,
            "status": "ENABLE",
            "$or": [{"email": email}, {"username": email}]
        })
        if user != None:
            if user.get("role") not in ["", "PARTICIPANT"]:
                response["desc"] = "This is a staff account. Use the admin login."
                return response
            # end if
            if check_password_hash(user.get("password") or "", raw_password):
                self.login_user(user.get("pkey", ""))
                response["status"] = "SUCCESS"
                return response
            # end if
            response["desc"] = "Username / email or password is not right"
            return response
        # end if
        if phone == "":
            response["desc"] = "Email or password is not right. If you registered without a password, also enter your phone to set one."
            return response
        # end if
        if len(raw_password) < 6:
            response["desc"] = "Password must be at least 6 characters"
            return response
        # end if
        part = self.mgdDB.db_participant.find_one({
            "email": email,
            "phone": phone,
            "is_deleted": False
        })
        if part == None:
            response["desc"] = "No registration matches that email and phone"
            return response
        # end if
        rec = database.new(self.mgdDB, "db_user")
        rec.put("fk_user_id", "")
        rec.put("username", email)
        rec.put("password", generate_password_hash(raw_password))
        rec.put("role", "PARTICIPANT")
        rec.put("name", part.get("full_name") or "")
        rec.put("phone", phone)
        rec.put("email", email)
        rec.put("status", "ENABLE")
        rec.insert()
        row = rec.get()
        pkey = row.get("pkey", "")
        self.mgdDB.db_participant.update_one(
            {"pkey": part.get("pkey")},
            {"$set": {"fk_user_id": pkey}}
        )
        self.login_user(pkey)
        response["status"] = "SUCCESS"
        return response
    # end def

    def get_login_page(self, error="", nxt="/dashboard"):
        allowed = [
            "/dashboard",
            "/dashboard/orders",
            "/dashboard/proposal",
            "/dashboard/events",
            "/dashboard/profile"
        ]
        if nxt not in allowed:
            nxt = "/dashboard"
        # end if
        return self.site.with_site({
            "form_error": error,
            "next_path": nxt
        })
    # end def

    def get_participant(self, user):
        if user == None:
            return None
        # end if
        rec = self.mgdDB.db_participant.find_one(
            {"fk_user_id": user.get("pkey", ""), "is_deleted": False},
            {"_id": 0}
        )
        if rec == None:
            rec = self.mgdDB.db_participant.find_one(
                {"email": (user.get("email") or "").lower(), "is_deleted": False},
                {"_id": 0}
            )
        # end if
        return rec
    # end def

    def is_self_pledge(self, item):
        if item == None:
            return False
        # end if
        source = (item.get("pledge_source") or "").strip().upper()
        if source == "SELF":
            return True
        # end if
        note = (item.get("note") or "").lower()
        if note.find("self pledge") >= 0:
            return True
        # end if
        return False
    # end def

    def proposal_raised_num(self, part):
        if part == None:
            return 0
        # end if
        total = 0
        for item in self.get_proposal_pledges(part):
            if (item.get("follow_status") or "") != "RECEIVED":
                continue
            # end if
            if self.is_self_pledge(item):
                continue
            # end if
            total = total + int(item.get("amount_num") or 0)
        # end for
        return total
    # end def

    def proposal_pending_num(self, part):
        if part == None:
            return 0
        # end if
        total = 0
        for item in self.get_proposal_pledges(part):
            if (item.get("follow_status") or "") == "RECEIVED":
                continue
            # end if
            if self.is_self_pledge(item):
                continue
            # end if
            total = total + int(item.get("amount_num") or 0)
        # end for
        return total
    # end def

    def self_contribution_num(self, part, received_only=True):
        if part == None:
            return 0
        # end if
        total = 0
        for item in self.get_proposal_pledges(part):
            if not self.is_self_pledge(item):
                continue
            # end if
            if received_only and (item.get("follow_status") or "") != "RECEIVED":
                continue
            # end if
            total = total + int(item.get("amount_num") or 0)
        # end for
        return total
    # end def

    def self_contribution_pending_num(self, part):
        if part == None:
            return 0
        # end if
        total = 0
        for item in self.get_proposal_pledges(part):
            if not self.is_self_pledge(item):
                continue
            # end if
            if (item.get("follow_status") or "") == "RECEIVED":
                continue
            # end if
            total = total + int(item.get("amount_num") or 0)
        # end for
        return total
    # end def

    def configured_shipping_service_fee_num(self):
        site = self.site.get_site() or {}
        value = site.get("shipping_service_fee_num")
        fee = int(10000 if value == None else value)
        return max(0, fee)
    # end def

    def order_shipping_service_fee_num(self, order):
        if "shipping_service_fee_num" in (order or {}):
            return max(0, int(order.get("shipping_service_fee_num") or 0))
        # end if
        return self.configured_shipping_service_fee_num()
    # end def

    def order_shipping_expense_num(self, order):
        return (
            int((order or {}).get("shipping_budget_num") or 0) +
            self.order_shipping_service_fee_num(order)
        )
    # end def

    def order_officer_shipping_deduction_display(self, order):
        handler = (order.get("shipping_handler") or "").strip().upper()
        if handler != "OFFICER":
            return 0, 0, 0, False
        # end if
        status = (order.get("shipping_request_status") or "").strip().upper()
        if status in ["SELF_ARRANGED", "NOT_REQUESTED", ""]:
            return 0, 0, 0, False
        # end if
        delivery = int(order.get("shipping_budget_num") or 0)
        fee = 0
        if order != None and "shipping_service_fee_num" in order:
            fee = max(0, int(order.get("shipping_service_fee_num") or 0))
        # end if
        if status in ["PROCESSING", "SHIPPED", "COMPLETED"]:
            fee = self.order_shipping_service_fee_num(order)
            total = delivery + fee
            return delivery, fee, total, True
        # end if
        if delivery > 0 or fee > 0:
            total = delivery + fee
            return delivery, fee, total, False
        # end if
        return 0, 0, 0, False
    # end def

    def shipping_expense_num(self, part, exclude_order_pkey=""):
        total = 0
        for order in self.get_referral_orders(part):
            if order.get("pkey") == exclude_order_pkey:
                continue
            # end if
            if (order.get("shipping_handler") or "").strip().upper() != "OFFICER":
                continue
            # end if
            if (order.get("shipping_request_status") or "").strip().upper() not in ["PROCESSING", "SHIPPED", "COMPLETED"]:
                continue
            # end if
            if (order.get("order_status") or "") == "Cancelled":
                continue
            # end if
            total = total + self.order_shipping_expense_num(order)
        # end for
        return total
    # end def

    def shipping_eligibility(self, part, order=None):
        merch = self.merch_raised_num(part)
        proposal = self.proposal_raised_num(part)
        own = self.self_contribution_num(part, True)
        exclude = (order or {}).get("pkey") or ""
        spent = self.shipping_expense_num(part, exclude)
        available = merch + proposal + own - spent
        if available < 0:
            available = 0
        # end if
        site = self.site.get_site() or {}
        minimum = self.site.shipping_minimum_num(site)
        return {
            "minimum_num": minimum,
            "minimum": self.format_rp(minimum),
            "merch_num": merch,
            "merch": self.format_rp(merch),
            "proposal_num": proposal,
            "proposal": self.format_rp(proposal),
            "self_contribution_num": own,
            "self_contribution": self.format_rp(own),
            "spent_num": spent,
            "spent": self.format_rp(spent),
            "available_num": available,
            "available": self.format_rp(available),
            "service_fee_num": self.configured_shipping_service_fee_num(),
            "service_fee": self.format_rp(self.configured_shipping_service_fee_num()),
            "eligible": available >= minimum
        }
    # end def

    def _progress_payload(self, target, raised, pending=0, message=""):
        remaining = target - raised
        if remaining < 0:
            remaining = 0
        # end if
        pct = 0
        if target > 0:
            pct = int(round(100.0 * raised / target))
        # end if
        marker_pct = pct
        if marker_pct > 100:
            marker_pct = 100
        # end if
        if marker_pct < 0:
            marker_pct = 0
        # end if
        over = raised - target
        if over < 0:
            over = 0
        # end if
        return {
            "target_num": target,
            "target": self.format_rp(target),
            "raised_num": raised,
            "raised": self.format_rp(raised),
            "pending_num": pending,
            "pending": self.format_rp(pending),
            "remaining_num": remaining,
            "remaining": self.format_rp(remaining),
            "over_num": over,
            "over": self.format_rp(over),
            "pct": pct,
            "marker_pct": marker_pct,
            "achieved": raised >= target and target > 0,
            "message": message
        }
    # end def

    def member_target_num(self, part):
        target = 0
        if part != None:
            target = int(part.get("contribution_num") or 0)
        # end if
        if target <= 0:
            site = self.site.get_site() or {}
            target = int(site.get("contribution_num") or 0)
        # end if
        if target <= 0:
            target = 2000000
        # end if
        return target
    # end def

    def combined_raised_num(self, part):
        merch = self.merch_raised_num(part)
        others = self.proposal_raised_num(part)
        self_amt = self.self_contribution_num(part, True)
        total = merch + others + self_amt - self.shipping_expense_num(part)
        if total < 0:
            total = 0
        # end if
        return total
    # end def

    def proposal_progress(self, part):
        target = self.member_target_num(part)
        merch = self.merch_raised_num(part)
        others = self.proposal_raised_num(part)
        self_amt = self.self_contribution_num(part, True)
        shipping_expense = self.shipping_expense_num(part)
        raised = merch + others + self_amt - shipping_expense
        if raised < 0:
            raised = 0
        # end if
        pending = self.proposal_pending_num(part) + self.self_contribution_pending_num(part)
        copy = self.dash_copy()
        message = (copy.get("proposal_progress_msg") or "").replace("{target}", self.format_rp(target))
        payload = self._progress_payload(target, raised, pending, message)
        payload["merch_num"] = merch
        payload["merch"] = self.format_rp(merch)
        payload["self_num"] = self_amt
        payload["self"] = self.format_rp(self_amt)
        payload["self_pending_num"] = self.self_contribution_pending_num(part)
        payload["self_pending"] = self.format_rp(payload["self_pending_num"])
        payload["others_num"] = others
        payload["others"] = self.format_rp(others)
        payload["shipping_expense_num"] = shipping_expense
        payload["shipping_expense"] = self.format_rp(shipping_expense)
        return payload
    # end def

    def order_counts_for_target(self, order):
        if order == None:
            return False
        # end if
        status = (order.get("order_status") or "").strip()
        pay = (order.get("payment_status") or "").strip()
        if status == "Cancelled":
            return False
        # end if
        # Only Paid (or further confirmed payment) accumulates to the shared target
        if pay == "Paid":
            return True
        # end if
        return False
    # end def

    def order_is_unpaid_lead(self, order):
        if order == None:
            return False
        # end if
        status = (order.get("order_status") or "").strip()
        pay = (order.get("payment_status") or "").strip()
        if status == "Cancelled":
            return False
        # end if
        if pay in ["Failed", "Refunded"]:
            return False
        # end if
        if pay == "Paid":
            return False
        # end if
        return True
    # end def

    def merch_raised_num(self, part):
        raised = 0
        for item in self.get_referral_orders(part):
            if not self.order_counts_for_target(item):
                continue
            # end if
            raised = raised + self.order_profit_num(item)
        # end for
        return raised
    # end def

    def order_profit_num(self, order):
        if order == None:
            return 0
        # end if
        if order.get("profit_total_num") != None:
            return int(order.get("profit_total_num") or 0)
        # end if
        total = 0
        has_line = False
        for item in (order.get("items") or []):
            if item.get("line_profit_num") != None:
                total = total + int(item.get("line_profit_num") or 0)
                has_line = True
                continue
            # end if
            slug = (item.get("slug") or "").strip()
            qty = int(item.get("qty") or 1)
            if qty < 1:
                qty = 1
            # end if
            unit = int(item.get("unit_price_num") or 0)
            if unit <= 0:
                line = int(item.get("line_num") or 0)
                if qty > 0:
                    unit = int(line / qty)
                # end if
            # end if
            bahan = 0
            if slug != "":
                product = self.mgdDB.db_product.find_one(
                    {"slug": slug, "is_deleted": False},
                    {"_id": 0, "bahan_baku_num": 1, "price_num": 1}
                )
                if product != None:
                    bahan = int(product.get("bahan_baku_num") or 0)
                    if unit <= 0:
                        unit = int(product.get("price_num") or 0)
                    # end if
                # end if
            # end if
            if bahan < 0:
                bahan = 0
            # end if
            unit_profit = unit - bahan
            if unit_profit < 0:
                unit_profit = 0
            # end if
            total = total + (unit_profit * qty)
            has_line = True
        # end for
        if has_line:
            return total
        # end if
        return int(order.get("subtotal_num") or 0)
    # end def

    def merch_order_count(self, part):
        count = 0
        for item in self.get_referral_orders(part):
            if not self.order_counts_for_target(item):
                continue
            # end if
            count = count + 1
        # end for
        return count
    # end def

    def unpaid_referral_leads(self, part):
        leads = []
        copy = self.dash_copy()
        for order in self.get_referral_orders(part):
            if not self.order_is_unpaid_lead(order):
                continue
            # end if
            name = (order.get("full_name") or "").strip() or "Buyer"
            phone = (order.get("phone") or "").strip()
            profit = self.order_profit_num(order)
            pay = (order.get("payment_status") or "Pending").strip() or "Pending"
            msg = (copy.get("lead_message") or "")
            msg = msg.replace("{name}", name).replace("{pay}", pay.lower())
            lead = {
                "pkey": order.get("pkey") or "",
                "order_id": order.get("order_id") or "",
                "full_name": name,
                "phone": phone,
                "email": (order.get("email") or "").strip(),
                "payment_status": pay,
                "order_status": (order.get("order_status") or "").strip(),
                "profit": self.format_rp(profit),
                "profit_num": profit,
                "message": msg
            }
            leads.append(lead)
        # end for
        return leads
    # end def

    def merch_progress(self, part):
        target = self.member_target_num(part)
        merch = self.merch_raised_num(part)
        others = self.proposal_raised_num(part)
        self_amt = self.self_contribution_num(part, True)
        shipping_expense = self.shipping_expense_num(part)
        raised = merch + others + self_amt - shipping_expense
        if raised < 0:
            raised = 0
        # end if
        order_count = self.merch_order_count(part)
        unpaid_leads = self.unpaid_referral_leads(part)
        unpaid_profit = 0
        for lead in unpaid_leads:
            unpaid_profit = unpaid_profit + int(lead.get("profit_num") or 0)
        # end for
        copy = self.dash_copy()
        message = (copy.get("merch_progress_msg") or "").replace("{target}", self.format_rp(target))
        payload = self._progress_payload(target, raised, unpaid_profit, message)
        payload["merch_num"] = merch
        payload["merch"] = self.format_rp(merch)
        payload["others_num"] = others
        payload["others"] = self.format_rp(others)
        payload["self_num"] = self_amt
        payload["self"] = self.format_rp(self_amt)
        payload["shipping_expense_num"] = shipping_expense
        payload["shipping_expense"] = self.format_rp(shipping_expense)
        payload["order_count"] = order_count
        payload["unpaid_leads"] = unpaid_leads
        payload["unpaid_count"] = len(unpaid_leads)
        payload["unpaid_profit"] = self.format_rp(unpaid_profit)
        payload["unpaid_profit_num"] = unpaid_profit
        return payload
    # end def

    def sync_merch_total(self, part):
        if part == None or not part.get("pkey"):
            return
        # end if
        sold = self.merch_raised_num(part)
        count = self.merch_order_count(part)
        self.mgdDB.db_participant.update_one(
            {"pkey": part.get("pkey")},
            {"$set": {
                "sales_total_num": sold,
                "sales_total": self.format_rp(sold),
                "sales_count": count
            }}
        )
    # end def

    def sync_proposal_total(self, part):
        if part == None or not part.get("pkey"):
            return
        # end if
        proposal = self.proposal_raised_num(part)
        self_amt = self.self_contribution_num(part, True)
        self.mgdDB.db_participant.update_one(
            {"pkey": part.get("pkey")},
            {"$set": {
                "proposal_total_num": proposal,
                "proposal_total": self.format_rp(proposal),
                "self_contribution_num": self_amt,
                "self_contribution": self.format_rp(self_amt)
            }}
        )
    # end def

    def save_member_pledge(self, params):
        response = {"status": "FAILED", "desc": ""}
        user = self.current_user()
        part = self.get_participant(user)
        if user == None or part == None:
            response["desc"] = "Login required"
            return response
        # end if
        if (part.get("member_type") or "AHC_MEMBER") != "AHC_MEMBER":
            response["desc"] = "Only AHC members can add a proposal pledge here"
            return response
        # end if
        raw = (params.get("commitment") or params.get("amount") or "").strip()
        digits = re.sub(r"[^0-9]", "", raw)
        if digits == "":
            response["desc"] = "Enter your commitment amount"
            return response
        # end if
        amount_num = int(digits)
        if amount_num <= 0:
            response["desc"] = "Amount must be more than zero"
            return response
        # end if
        name = (params.get("name") or "").strip() or (part.get("full_name") or user.get("name") or "").strip()
        phone = (params.get("phone") or "").strip() or (part.get("phone") or user.get("phone") or "").strip()
        if name == "":
            response["desc"] = "Name is required"
            return response
        # end if
        code = (part.get("referral_code") or "").strip().lower()
        rec = database.new(self.mgdDB, "db_donor")
        rec.put("name", name)
        rec.put("phone", phone)
        rec.put("amount_label", self.format_rp(amount_num))
        rec.put("amount_num", amount_num)
        rec.put("score", amount_num)
        rec.put("note", "Self pledge from member dashboard")
        rec.put("referral_code", code)
        rec.put("fk_referrer_id", part.get("pkey") or "")
        rec.put("fk_referrer_reg_id", part.get("reg_id") or "")
        rec.put("pledge_source", "SELF")
        rec.put("follow_status", "FOLLOW_UP")
        rec.put("status", "HIDDEN")
        rec.insert()
        # Force follow-up only — never auto-Received / public
        saved = rec.get()
        pkey = saved.get("pkey") or ""
        if pkey != "":
            self.mgdDB.db_donor.update_one(
                {"pkey": pkey},
                {"$set": {
                    "pledge_source": "SELF",
                    "follow_status": "FOLLOW_UP",
                    "status": "HIDDEN"
                }}
            )
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def

    def order_bahan_num(self, order):
        if order == None:
            return 0
        # end if
        if order.get("bahan_baku_total_num") != None:
            return int(order.get("bahan_baku_total_num") or 0)
        # end if
        total = 0
        has_line = False
        for item in (order.get("items") or []):
            if item.get("line_bahan_baku_num") != None:
                total = total + int(item.get("line_bahan_baku_num") or 0)
                has_line = True
                continue
            # end if
            slug = (item.get("slug") or "").strip()
            qty = int(item.get("qty") or 1)
            if qty < 1:
                qty = 1
            # end if
            bahan = 0
            if slug != "":
                product = self.mgdDB.db_product.find_one(
                    {"slug": slug, "is_deleted": False},
                    {"_id": 0, "bahan_baku_num": 1}
                )
                if product != None:
                    bahan = int(product.get("bahan_baku_num") or 0)
                # end if
            # end if
            if bahan < 0:
                bahan = 0
            # end if
            total = total + (bahan * qty)
            has_line = True
        # end for
        if has_line:
            return total
        # end if
        sale = int(order.get("subtotal_num") or 0)
        profit = self.order_profit_num(order)
        left = sale - profit
        if left < 0:
            left = 0
        # end if
        return left
    # end def

    def localized_status(self, status, copy=None):
        labels = copy or self.dash_copy()
        key = {
            "Pending Payment": "status_pending_payment",
            "Preorder": "status_preorder",
            "Paid": "status_paid",
            "Ready": "status_ready",
            "Processing": "status_processing",
            "Shipped": "status_shipped",
            "Completed": "status_completed",
            "Cancelled": "status_cancelled",
            "Pending": "status_pending"
        }.get(status)
        if key == None:
            return status
        # end if
        return labels.get(key) or status
    # end def

    def decorate_referral_orders(self, orders):
        rows = []
        copy = self.dash_copy()
        for order in orders:
            sale_num = int(order.get("subtotal_num") or 0)
            bahan_num = self.order_bahan_num(order)
            profit_num = self.order_profit_num(order)
            why = "Your credit is profit only: sale − bahan baku."
            if sale_num > 0:
                why = (
                    self.format_rp(sale_num) + " sale − " +
                    self.format_rp(bahan_num) + " bahan baku = " +
                    self.format_rp(profit_num) + " profit"
                )
            # end if
            product_labels = []
            sku_labels = []
            line_rows = []
            order_status = (order.get("order_status") or "").strip()
            for idx, line in enumerate(order.get("items") or []):
                name = (line.get("name") or "").strip()
                slug = (line.get("slug") or "").strip()
                qty = int(line.get("qty") or 1)
                sku = (line.get("sku") or "").strip()
                size = (line.get("size") or "").strip()
                color = (line.get("color") or "").strip()
                if sku == "" and slug != "":
                    product = self.mgdDB.db_product.find_one(
                        {"slug": slug, "is_deleted": False},
                        {"_id": 0, "sku": 1, "name": 1}
                    )
                    if product != None:
                        sku = (product.get("sku") or "").strip()
                        if name == "":
                            name = (product.get("name") or "").strip()
                        # end if
                    # end if
                # end if
                if name == "":
                    name = slug or "Item"
                # end if
                label = name
                if size != "":
                    label = label + " · " + size
                # end if
                if color != "":
                    label = label + " · " + color
                # end if
                if qty > 1:
                    label = label + " × " + str(qty)
                # end if
                product_labels.append(label)
                if sku != "":
                    sku_labels.append(sku)
                else:
                    sku_labels.append("—")
                # end if
                line_status = (line.get("line_status") or "").strip()
                if line_status == "":
                    if line.get("is_preorder"):
                        line_status = "Preorder"
                    else:
                        line_status = order_status or "Pending Payment"
                    # end if
                # end if
                line_rows.append({
                    "idx": idx,
                    "name": name,
                    "size": size,
                    "color": color,
                    "qty": qty,
                    "sku": sku if sku != "" else "—",
                    "unit_price": line.get("unit_price") or self.format_rp(line.get("unit_price_num")),
                    "line_price": line.get("line_price") or self.format_rp(line.get("line_num")),
                    "line_status": line_status,
                    "line_status_label": self.localized_status(line_status, copy),
                    "line_status_opts": self.order_status_options(line_status),
                    "is_preorder": line.get("is_preorder") == True or line_status == "Preorder",
                    "preorder_eta": (line.get("preorder_eta") or "").strip()
                })
            # end for
            row = dict(order)
            if order.get("shipping_handler") == "OFFICER":
                saved_service_fee_num = self.order_shipping_service_fee_num(order)
                row["shipping_service_fee_num"] = saved_service_fee_num
                row["shipping_service_fee"] = self.format_rp(saved_service_fee_num)
            # end if
            row["sale"] = self.format_rp(sale_num)
            row["sale_num"] = sale_num
            row["bahan_baku"] = self.format_rp(bahan_num)
            row["bahan_baku_num"] = bahan_num
            row["profit"] = self.format_rp(profit_num)
            row["profit_num"] = profit_num
            shipping_delivery_num, shipping_service_fee_num, shipping_deduction_num, shipping_deduction_locked = (
                self.order_officer_shipping_deduction_display(order)
            )
            net_profit_num = profit_num - shipping_deduction_num
            net_profit = self.format_rp(abs(net_profit_num))
            if net_profit_num < 0:
                net_profit = "−" + net_profit
            # end if
            row["shipping_deduction_active"] = shipping_deduction_num > 0
            row["shipping_deduction_locked"] = shipping_deduction_locked
            row["shipping_deduction_num"] = shipping_deduction_num
            row["shipping_deduction"] = self.format_rp(shipping_deduction_num)
            row["shipping_delivery_num"] = shipping_delivery_num
            row["shipping_delivery"] = self.format_rp(shipping_delivery_num)
            row["shipping_service_fee_deduction_num"] = shipping_service_fee_num
            row["shipping_service_fee_deduction"] = self.format_rp(shipping_service_fee_num)
            if int(row.get("shipping_service_fee_num") or 0) > 0:
                row["shipping_service_fee"] = (
                    row.get("shipping_service_fee") or
                    self.format_rp(row.get("shipping_service_fee_num"))
                )
            # end if
            row["net_profit_num"] = net_profit_num
            row["net_profit"] = net_profit
            row["address_rows"] = self.address.display_rows(order)
            row["shipping_address_rows"] = self.address.display_rows(order, "shipping_")
            shipping_status = (order.get("shipping_request_status") or "").strip().upper()
            shipping_label_key = {
                "REQUESTED": "shipping_status_requested",
                "PROCESSING": "shipping_status_processing",
                "SHIPPED": "shipping_status_shipped",
                "COMPLETED": "shipping_status_completed",
                "SELF_ARRANGED": "shipping_status_self"
            }.get(shipping_status, "shipping_status_empty")
            row["shipping_status_label"] = copy.get(shipping_label_key)
            row["order_status_label"] = self.localized_status(order.get("order_status") or "", copy)
            row["payment_status_label"] = self.localized_status(order.get("payment_status") or "", copy)
            row["profit_why"] = why
            row["product_label"] = ", ".join(product_labels) if product_labels != [] else "—"
            row["sku_label"] = ", ".join(sku_labels) if sku_labels != [] else "—"
            row["line_rows"] = line_rows
            row["order_status_opts"] = self.order_status_options(order.get("order_status") or "")
            row["pay_status_opts"] = self.order_pay_options(order.get("payment_status") or "")
            has_preorder = order.get("has_preorder") == True
            preorder_eta = (order.get("preorder_eta") or "").strip()
            if not has_preorder:
                for line in (order.get("items") or []):
                    if line.get("is_preorder"):
                        has_preorder = True
                        if preorder_eta == "":
                            preorder_eta = (line.get("preorder_eta") or "").strip()
                        # end if
                    # end if
                # end for
            # end if
            row["has_preorder"] = has_preorder
            row["preorder_eta"] = preorder_eta
            row["counts_for_target"] = self.order_counts_for_target(order)
            row["is_unpaid_lead"] = self.order_is_unpaid_lead(order)
            rows.append(row)
        # end for
        return rows
    # end def

    def order_status_options(self, current=""):
        opts = list(self.ORDER_STATUSES)
        if current != "" and current not in opts:
            opts.insert(0, current)
        # end if
        return opts
    # end def

    def order_pay_options(self, current=""):
        return list(self.ORDER_PAY_STATUSES)
    # end def

    def rollup_order_status(self, line_statuses, fallback=""):
        statuses = []
        for st in line_statuses or []:
            clean = (st or "").strip()
            if clean != "":
                statuses.append(clean)
            # end if
        # end for
        if statuses == []:
            return fallback or "Pending Payment"
        # end if
        unique = list(set(statuses))
        if len(unique) == 1:
            return unique[0]
        # end if
        # Mixed sizes: prefer the least-complete active status for the order header
        rank = {
            "Pending Payment": 0,
            "Preorder": 1,
            "Paid": 2,
            "Ready": 3,
            "Processing": 4,
            "Shipped": 5,
            "Completed": 6,
            "Cancelled": 7
        }
        active = [s for s in statuses if s != "Cancelled"]
        if active == []:
            return "Cancelled"
        # end if
        best = active[0]
        for s in active:
            if rank.get(s, 99) < rank.get(best, 99):
                best = s
            # end if
        # end for
        return best
    # end def

    def is_member_referral_order(self, part, order):
        if part == None or order == None:
            return False
        # end if
        pkey = part.get("pkey") or ""
        code = (part.get("referral_code") or "").strip().lower()
        if pkey != "" and (order.get("fk_referrer_id") or "") == pkey:
            return True
        # end if
        if code != "" and (order.get("referral_code") or "").strip().lower() == code:
            return True
        # end if
        return False
    # end def

    def update_referral_order(self, params):
        response = {"status": "FAILED", "desc": ""}
        user = self.current_user()
        part = self.get_participant(user)
        if user == None or part == None:
            response["desc"] = "Login required"
            return response
        # end if
        if (part.get("member_type") or "AHC_MEMBER") != "AHC_MEMBER":
            response["desc"] = "Only AHC members can update referral orders"
            return response
        # end if
        pkey = (params.get("pkey") or "").strip()
        if pkey == "":
            response["desc"] = "Order not found"
            return response
        # end if
        order = self.mgdDB.db_order.find_one(
            {"pkey": pkey, "is_deleted": False},
            {"_id": 0}
        )
        if order == None or not self.is_member_referral_order(part, order):
            response["desc"] = "Order not found for your referral"
            return response
        # end if
        if order.get("shipping_handler") == "OFFICER":
            response["desc"] = self.dash_copy().get("shipping_member_edits_locked")
            return response
        # end if
        payment_status = (params.get("payment_status") or "").strip()
        if payment_status not in self.ORDER_PAY_STATUSES:
            payment_status = order.get("payment_status") or "Pending"
        # end if
        items = []
        raw_items = order.get("items") or []
        for idx, line in enumerate(raw_items):
            row = dict(line)
            key = "line_status_" + str(idx)
            st = (params.get(key) or "").strip()
            if st not in self.ORDER_STATUSES:
                st = (row.get("line_status") or "").strip()
                if st == "":
                    if row.get("is_preorder"):
                        st = "Preorder"
                    else:
                        st = order.get("order_status") or "Pending Payment"
                    # end if
                # end if
                if st not in self.ORDER_STATUSES:
                    st = "Pending Payment"
                # end if
            # end if
            row["line_status"] = st
            items.append(row)
        # end for
        # Main order status only changes when "Set all lines to" was used
        order_status = order.get("order_status") or "Pending Payment"
        header_status = (params.get("order_status") or "").strip()
        apply_all = (params.get("apply_all_lines") or "") in ["1", "YES", "true", "on"]
        if apply_all and header_status in self.ORDER_STATUSES:
            order_status = header_status
            for row in items:
                row["line_status"] = header_status
            # end for
        # end if
        updates = {
            "items": items,
            "order_status": order_status,
            "payment_status": payment_status
        }
        if (params.get("action") or "") == "delivery_location":
            addr = self.address.collect(params)
            addr_check = self.address.validate(addr)
            if addr_check.get("status") != "SUCCESS":
                response["desc"] = addr_check.get("desc") or "Alamat pengiriman belum lengkap"
                return response
            # end if
            updates.update(addr)
        # end if
        self.mgdDB.db_order.update_one(
            {"pkey": pkey},
            {"$set": updates}
        )
        self.sync_merch_total(part)
        response["status"] = "SUCCESS"
        return response
    # end def

    def save_shipping_request(self, params):
        response = {"status": "FAILED", "desc": ""}
        copy = self.dash_copy()
        user = self.current_user()
        part = self.get_participant(user)
        if user == None or part == None:
            response["desc"] = "Login required"
            return response
        # end if
        pkey = (params.get("pkey") or "").strip()
        order = self.mgdDB.db_order.find_one(
            {"pkey": pkey, "is_deleted": False},
            {"_id": 0}
        )
        if order == None or not self.is_member_referral_order(part, order):
            response["desc"] = "Order not found for your referral"
            return response
        # end if
        handler = (params.get("shipping_handler") or "").strip().upper()
        if handler not in self.SHIPPING_HANDLERS:
            response["desc"] = copy.get("shipping_select_error")
            return response
        # end if
        current_handler = (order.get("shipping_handler") or "").strip().upper()
        if handler == "SELF":
            if current_handler == "OFFICER":
                response["desc"] = copy.get("shipping_cancel_locked")
                return response
            # end if
            self.mgdDB.db_order.update_one(
                {"pkey": pkey},
                {"$set": {
                    "shipping_handler": "SELF",
                    "shipping_request_status": "SELF_ARRANGED",
                    "shipping_service_fee": "",
                    "shipping_service_fee_num": 0
                }}
            )
            response["status"] = "SUCCESS"
            return response
        # end if
        eligibility = self.shipping_eligibility(part, order)
        if current_handler != "OFFICER" and not eligibility.get("eligible"):
            response["desc"] = copy.get("shipping_minimum_error").replace(
                "{minimum}", eligibility.get("minimum")
            )
            return response
        # end if
        if (params.get("shipping_confirm_info") or "") not in ["1", "YES", "true", "on", "True"]:
            response["desc"] = copy.get("shipping_confirm_error")
            return response
        # end if
        if (params.get("shipping_confirm_process") or "") not in ["1", "YES", "true", "on", "True"]:
            response["desc"] = copy.get("shipping_process_confirm_error")
            return response
        # end if
        same_buyer = (params.get("shipping_recipient_same_buyer") or "") in ["1", "YES", "true", "on", "True"]
        if same_buyer:
            shipping_name = (order.get("full_name") or "").strip()
            shipping_phone = (order.get("phone") or "").strip()
            ship_addr = self.address.from_record(order)
        else:
            shipping_name = (params.get("shipping_name") or "").strip()
            shipping_phone = (params.get("shipping_phone") or "").strip()
            ship_addr = self.address.collect(params, "shipping_")
            addr_check = self.address.validate(ship_addr)
            if addr_check.get("status") != "SUCCESS":
                response["desc"] = addr_check.get("desc") or copy.get("shipping_recipient_error")
                return response
            # end if
        # end if
        if shipping_name == "" or shipping_phone == "" or (ship_addr.get("address") or "") == "":
            response["desc"] = copy.get("shipping_recipient_error")
            return response
        # end if
        service_fee_num = self.configured_shipping_service_fee_num()
        shipping_set = {
            "shipping_handler": "OFFICER",
            "shipping_recipient_same_buyer": same_buyer,
            "shipping_name": shipping_name,
            "shipping_phone": shipping_phone,
            "shipping_package_note": (params.get("shipping_package_note") or "").strip(),
            "shipping_request_status": "REQUESTED",
            "shipping_service_fee": self.format_rp(service_fee_num),
            "shipping_service_fee_num": service_fee_num
        }
        shipping_set.update(self.address.prefixed(ship_addr, "shipping_"))
        self.mgdDB.db_order.update_one(
            {"pkey": pkey},
            {"$set": shipping_set}
        )
        response["status"] = "SUCCESS"
        return response
    # end def

    def complete_officer_shipping_order(self, params):
        response = {"status": "FAILED", "desc": ""}
        copy = self.dash_copy()
        user = self.current_user()
        part = self.get_participant(user)
        pkey = (params.get("pkey") or "").strip()
        order = self.mgdDB.db_order.find_one(
            {"pkey": pkey, "is_deleted": False},
            {"_id": 0}
        )
        if user == None or part == None or order == None or not self.is_member_referral_order(part, order):
            response["desc"] = "Order not found for your referral"
            return response
        # end if
        if order.get("shipping_handler") != "OFFICER":
            response["desc"] = copy.get("shipping_wait_shipped")
            return response
        # end if
        shipping_status = (order.get("shipping_request_status") or "").strip().upper()
        if shipping_status not in ["SHIPPED", "COMPLETED"]:
            response["desc"] = copy.get("shipping_wait_shipped")
            return response
        # end if
        items = []
        for line in order.get("items") or []:
            row = dict(line)
            row["line_status"] = "Completed"
            items.append(row)
        # end for
        self.mgdDB.db_order.update_one(
            {"pkey": pkey},
            {"$set": {
                "items": items,
                "order_status": "Completed",
                "shipping_request_status": "COMPLETED"
            }}
        )
        response["status"] = "SUCCESS"
        return response
    # end def

    def get_referral_orders(self, part, status="", payment="", contact=""):
        if part == None:
            return []
        # end if
        code = (part.get("referral_code") or "").strip().lower()
        pkey = part.get("pkey") or ""
        clauses = []
        if pkey != "":
            clauses.append({"fk_referrer_id": pkey})
        # end if
        if code != "":
            clauses.append({"referral_code": code})
        # end if
        if clauses == []:
            return []
        # end if
        and_parts = [
            {"is_deleted": False},
            {"$or": clauses}
        ]
        status_clean = (status or "").strip()
        if status_clean != "" and status_clean != "ALL":
            # Match order header OR any size/line status
            and_parts.append({
                "$or": [
                    {"order_status": status_clean},
                    {"items.line_status": status_clean}
                ]
            })
        # end if
        payment_clean = (payment or "").strip()
        if payment_clean != "" and payment_clean != "ALL":
            and_parts.append({"payment_status": payment_clean})
        # end if
        contact_clean = (contact or "").strip()
        if contact_clean != "":
            # Escape regex special chars lightly
            safe = re.escape(contact_clean)
            and_parts.append({
                "$or": [
                    {"full_name": {"$regex": safe, "$options": "i"}},
                    {"email": {"$regex": safe, "$options": "i"}},
                    {"phone": {"$regex": safe, "$options": "i"}}
                ]
            })
        # end if
        query = {"$and": and_parts}
        return list(self.mgdDB.db_order.find(
            query,
            {"_id": 0}
        ).sort("rec_timestamp", -1))
    # end def

    def get_referral_order_detail(self, part, order_ref):
        ref = (order_ref or "").strip()
        if ref == "":
            return None
        # end if
        for order in self.get_referral_orders(part):
            if order.get("pkey") == ref or order.get("order_id") == ref:
                rows = self.decorate_referral_orders([order])
                if rows != []:
                    return rows[0]
                # end if
            # end if
        # end for
        return None
    # end def

    def get_proposal_pledges(self, part):
        if part == None:
            return []
        # end if
        code = (part.get("referral_code") or "").strip().lower()
        pkey = part.get("pkey") or ""
        clauses = []
        if pkey != "":
            clauses.append({"fk_referrer_id": pkey})
        # end if
        if code != "":
            clauses.append({"referral_code": code})
        # end if
        if clauses == []:
            return []
        # end if
        return list(self.mgdDB.db_donor.find(
            {"is_deleted": False, "$or": clauses},
            {"_id": 0}
        ).sort("rec_timestamp", -1))
    # end def

    def get_orders(self, user):
        if user == None:
            return []
        # end if
        email = (user.get("email") or "").lower()
        sid = ""
        if has_request_context():
            sid = session.get("cart_sid", "")
        # end if
        clauses = [{"fk_user_id": user.get("pkey", "")}]
        if email != "":
            clauses.append({"email": email})
        # end if
        if sid != "":
            clauses.append({"session_id": sid})
        # end if
        recs = list(self.mgdDB.db_order.find(
            {"is_deleted": False, "$or": clauses},
            {"_id": 0}
        ).sort("rec_timestamp", -1))
        return recs
    # end def

    def get_events(self):
        recs = list(self.mgdDB.db_event.find(
            {"is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def base_data(self, page, extra=None):
        user = self.current_user()
        part = self.get_participant(user)
        orders = self.get_orders(user)
        events = self.get_events()
        upcoming = []
        for item in events:
            status = item.get("event_status") or ""
            if status != "Registration Closed":
                upcoming.append(item)
            # end if
        # end for
        referral_orders = []
        proposal_pledges = []
        proposal_progress = None
        merch_progress = None
        is_ahc = False
        order_status_filter = ""
        payment_status_filter = ""
        order_contact_q = ""
        if extra != None:
            order_status_filter = (extra.get("order_status_filter") or "").strip()
            payment_status_filter = (extra.get("payment_status_filter") or "").strip()
            order_contact_q = (extra.get("order_contact_q") or "").strip()
        # end if
        if part != None and (part.get("member_type") or "AHC_MEMBER") == "AHC_MEMBER":
            is_ahc = True
            referral_orders = self.decorate_referral_orders(
                self.get_referral_orders(
                    part,
                    order_status_filter,
                    payment_status_filter,
                    order_contact_q
                )
            )
            proposal_pledges = self.get_proposal_pledges(part)
            self.sync_merch_total(part)
            self.sync_proposal_total(part)
            part = self.get_participant(user)
            proposal_progress = self.proposal_progress(part)
            merch_progress = self.merch_progress(part)
        # end if
        nav = self.dash_nav(is_ahc)
        copy = self.dash_copy()
        payload = {
            "dash_page": page,
            "dash_nav": nav,
            "dash": copy,
            "user": user,
            "participant": part,
            "is_ahc_member": is_ahc,
            "orders": orders,
            "referral_orders": referral_orders,
            "order_status_filter": order_status_filter,
            "order_status_filters": list(self.ORDER_STATUSES),
            "payment_status_filter": payment_status_filter,
            "payment_status_filters": list(self.ORDER_PAY_STATUSES),
            "order_contact_q": order_contact_q,
            "proposal_pledges": proposal_pledges,
            "proposal_progress": proposal_progress,
            "merch_progress": merch_progress,
            "events": events,
            "upcoming_events": upcoming,
            "opening_message": copy.get("opening_message") or "",
            "form_error": "",
            "form_ok": False
        }
        if extra != None:
            payload.update(extra)
        # end if
        return self.site.with_site(payload)
    # end def

    def save_profile(self, params):
        response = {"status": "FAILED", "desc": ""}
        user = self.current_user()
        if user == None:
            response["desc"] = "Login required"
            return response
        # end if
        name = (params.get("full_name") or "").strip()
        phone = (params.get("phone") or "").strip()
        if name == "":
            response["desc"] = "Name is required"
            return response
        # end if
        self.mgdDB.db_user.update_one(
            {"pkey": user.get("pkey")},
            {"$set": {"name": name, "phone": phone}}
        )
        part = self.get_participant(user)
        if part != None:
            fields = {
                "full_name": name,
                "phone": phone,
                "address": (params.get("address") or "").strip(),
                "city": (params.get("city") or "").strip(),
                "emergency_contact": (params.get("emergency_contact") or "").strip(),
                "shirt_size": (params.get("shirt_size") or "").strip()
            }
            if (part.get("member_type") or "") == "AHC_MEMBER":
                raw = (params.get("referral_code") or "").strip().lower()
                clean = re.sub(r"[^a-z0-9]", "", raw)
                if clean != "":
                    if len(clean) < 4:
                        response["desc"] = "Referral code must be at least 4 letters or numbers"
                        return response
                    # end if
                    other = self.mgdDB.db_participant.find_one({
                        "referral_code": clean,
                        "is_deleted": False,
                        "pkey": {"$ne": part.get("pkey")}
                    })
                    if other != None:
                        response["desc"] = "That referral code is already used"
                        return response
                    # end if
                    fields["referral_code"] = clean
                # end if
            # end if
            self.mgdDB.db_participant.update_one(
                {"pkey": part.get("pkey")},
                {"$set": fields}
            )
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def
# end class
