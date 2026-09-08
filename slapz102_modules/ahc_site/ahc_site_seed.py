import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from werkzeug.security import generate_password_hash

class ahc_site_seed:

    mgdDB = database.get_db_conn(config.mainDB)
    _did_seed = False

    def __init__(self, app=None):
        self.webapp = app
    # end def

    def ensure_counter(self):
        existing = self.mgdDB.db_unique_counter.find_one({})
        if existing == None:
            self.mgdDB.db_unique_counter.insert_one({"counter": 1})
        # end if
    # end def

    def _insert(self, table, fields):
        rec = database.new(self.mgdDB, table)
        for key in fields:
            rec.put(key, fields[key])
        # end for
        rec.insert()
    # end def

    def _insert_missing(self, table, match, fields):
        existing = self.mgdDB[table].find_one(match)
        if existing == None:
            self._insert(table, fields)
        # end if
    # end def

    def _about_site_fields(self):
        return {
            "about_fraco": "FRACO is the community of the class of 2017. We organize programs, merchandise, partnerships, and the Alumni Home Coming calendar so alumni, students, partners, and the public have one place to reconnect.",
            "about_purpose": "Alumni Home Coming 2027 (AHC 2027) is FRACO's main event — ten years on from graduation in 2017. It is a community platform, not a one-day landing page, made to reconnect the class of 2017, inspire the next step, and give back through education, work, and gathering.",
            "about_audience": "It is first for FRACO alumni who graduated in 2017, and also for students looking for a next step, partners who want to build with us, and anyone in the community who wants to take part.",
            "about_activities": "The public program includes University Fair, Career Workshop, Spiritual Affairs, and Events — with FRACO merchandise, member kits, and partnership tracks running alongside.",
            "about_impact": "The work is meant to leave something standing: relationships, opportunity, and a shared record of what the class of 2017 can still put together."
        }
    # end def

    def _brand_site_fields(self):
        fields = {
            "name": "FRACO",
            "event_name": "AHC 2027",
            "event_full_name": "Alumni Home Coming 2027",
            "graduation_year": "2017",
            "class_label": "Class of 2017",
            "tagline": "Reconnect. Inspire. Give Back.",
            "tagline_id": "Reconnect. Inspire. Give Back.",
            "presented_by": "A FRACO community · Class of 2017",
            "presented_by_id": "Komunitas FRACO · Angkatan 2017",
            "subtitle": "FRACO is the class of 2017. Alumni Home Coming 2027 brings alumni, students, partners, and the community back together through programs, collaboration, and shared experience.",
            "subtitle_id": "FRACO adalah angkatan 2017. Alumni Home Coming 2027 mempertemukan alumni, mahasiswa, mitra, dan komunitas melalui program, kolaborasi, dan pengalaman bersama.",
            "description": "FRACO is the community of alumni who graduated in 2017. Alumni Home Coming 2027 (AHC 2027) is our gathering — a chance to reconnect, inspire, and give back.",
            "description_id": "FRACO adalah komunitas alumni lulusan 2017. Alumni Home Coming 2027 (AHC 2027) adalah pertemuan kami — kesempatan untuk reconnect, inspire, dan give back.",
            "announcement": "FRACO · CLASS OF 2017 · ALUMNI HOME COMING 2027 · CONTRIBUTION OPEN",
            "announcement_id": "FRACO · ANGKATAN 2017 · ALUMNI HOME COMING 2027 · KONTRIBUSI DIBUKA"
        }
        fields.update(self._about_site_fields())
        return fields
    # end def

    def ensure_site_brand(self):
        site = self.mgdDB.db_site.find_one({"is_deleted": False})
        if site == None:
            return
        # end if
        brand = self._brand_site_fields()
        patch = {}
        for key in brand:
            if (site.get(key) or "").strip() == "":
                patch[key] = brand.get(key) or ""
            # end if
        # end for
        if patch != {}:
            self.mgdDB.db_site.update_one(
                {"pkey": site["pkey"]},
                {"$set": patch}
            )
        # end if
    # end def

    def ensure_product_names(self):
        details = {
            "ahc-tee": {
                "name": "FRACO Tee",
                "price": "Rp 185.000",
                "price_num": 185000,
                "description": "A heavyweight tee for the class of 2017. Printed for Alumni Home Coming 2027.",
                "colors": ["Black", "White"],
                "images": [
                    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&q=80&w=1200",
                    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&q=80&w=1200"
                ],
                "category": "Apparel",
                "availability": "In Stock",
                "stock": 40
            },
            "ahc-cap": {
                "name": "FRACO Cap",
                "price": "Rp 120.000",
                "price_num": 120000,
                "description": "A structured cap with the FRACO mark. Everyday kit for the gathering.",
                "colors": ["Black"],
                "images": [
                    "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?auto=format&fit=crop&q=80&w=1200"
                ],
                "category": "Accessories",
                "availability": "In Stock",
                "stock": 30
            },
            "member-kit": {
                "name": "FRACO Member Kit",
                "price": "Included",
                "price_num": 0,
                "description": "Tee, ID card, and lanyard for confirmed participants. Not sold separately.",
                "colors": [],
                "images": [
                    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&q=80&w=1200"
                ],
                "category": "Member Kit",
                "availability": "For Participants",
                "stock": 0
            },
            "ahc-tote": {
                "name": "FRACO Tote",
                "price": "Rp 95.000",
                "price_num": 95000,
                "description": "A canvas tote for the class of 2017. Carry the gathering with you.",
                "colors": ["Natural"],
                "images": [
                    "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=1200"
                ],
                "category": "Accessories",
                "availability": "In Stock",
                "stock": 25
            }
        }
        for slug in details:
            self.mgdDB.db_product.update_one(
                {"slug": slug, "is_deleted": False},
                {"$set": details[slug]}
            )
        # end for
        self.mgdDB.db_program.update_one(
            {"slug": "spiritual-affairs", "is_deleted": False},
            {"$set": {"description": "Gatherings, vespers, and quiet space inside the FRACO calendar."}}
        )
        self.mgdDB.db_program.update_one(
            {"slug": "events", "is_deleted": False},
            {"$set": {"description": "The public program of Alumni Home Coming 2027 — upcoming, open, and completed."}}
        )
        self.mgdDB.db_update.update_one(
            {"slug": "registration-open", "is_deleted": False},
            {"$set": {"excerpt": "Join FRACO — class of 2017 — for Alumni Home Coming 2027. Full payment or installment from September through March."}}
        )
    # end def

    def seed_if_empty(self):
        if ahc_site_seed._did_seed:
            return
        # end if
        self.ensure_counter()
        if self.mgdDB.db_site.find_one({"is_deleted": False}) == None:
            site_row = {
                "phone": "6285258175916",
                "whatsapp_url": "https://api.whatsapp.com/send?phone=6285258175916",
                "contribution": "Rp 2.000.000",
                "contribution_num": 2000000,
                "status": "ENABLE"
            }
            site_row.update(self._brand_site_fields())
            self._insert("db_site", site_row)
        # end if
        self.ensure_site_brand()
        products = [
            {"slug": "ahc-tee", "name": "FRACO Tee", "price": "Rp 185.000", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&q=80&w=800", "sizes": ["S", "M", "L", "XL"], "category": "Apparel", "availability": "In Stock", "stock": 40, "status": "ACTIVE"},
            {"slug": "ahc-cap", "name": "FRACO Cap", "price": "Rp 120.000", "image": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?auto=format&fit=crop&q=80&w=800", "sizes": ["One Size"], "category": "Accessories", "availability": "In Stock", "stock": 30, "status": "ACTIVE"},
            {"slug": "member-kit", "name": "FRACO Member Kit", "price": "Included", "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&q=80&w=800", "sizes": ["S", "M", "L", "XL"], "category": "Member Kit", "availability": "For Participants", "stock": 0, "status": "ACTIVE"},
            {"slug": "ahc-tote", "name": "FRACO Tote", "price": "Rp 95.000", "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=800", "sizes": ["One Size"], "category": "Accessories", "availability": "In Stock", "stock": 25, "status": "ACTIVE"}
        ]
        for item in products:
            self._insert_missing("db_product", {"slug": item["slug"]}, item)
        # end for
        programs = [
            {"slug": "university-fair", "title": "University Fair", "description": "Connect students with universities and educational opportunities.", "image": "https://images.unsplash.com/photo-1523050854058-8cb90180b9ae?auto=format&fit=crop&q=80&w=1200", "status": "PUBLISHED"},
            {"slug": "career-workshop", "title": "Career Workshop", "description": "Speakers, industries, and practical sessions for the next step.", "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&q=80&w=1200", "status": "PUBLISHED"},
            {"slug": "spiritual-affairs", "title": "Spiritual Affairs", "description": "Gatherings, vespers, and quiet space inside the FRACO calendar.", "image": "https://images.unsplash.com/photo-1507692049790-de58290a4334?auto=format&fit=crop&q=80&w=1200", "status": "PUBLISHED"},
            {"slug": "events", "title": "Events", "description": "The public program of Alumni Home Coming 2027 — upcoming, open, and completed.", "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=1200", "status": "PUBLISHED"}
        ]
        for item in programs:
            self._insert_missing("db_program", {"slug": item["slug"]}, item)
        # end for
        updates = [
                {"slug": "registration-open", "title": "Participant contribution is open", "date": "1 September 2026", "category": "Announcements", "excerpt": "Join FRACO — class of 2017 — for Alumni Home Coming 2027. Full payment or installment from September through March.", "image": "https://images.unsplash.com/photo-1529156069898-49953e654ee0?auto=format&fit=crop&q=80&w=1200", "content": "", "status": "PUBLISHED"},
            {"slug": "vendor-listing", "title": "Vendor listing begins this month", "date": "3 September 2026", "category": "Event Updates", "excerpt": "Catering, AV, decoration, and support partners can apply now.", "image": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&q=80&w=1200", "content": "", "status": "PUBLISHED"},
            {"slug": "kit-preview", "title": "Member kit preview", "date": "5 September 2026", "category": "Behind the Scenes", "excerpt": "Tee, ID card, and lanyard — the kit the Member Kit division is building.", "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&q=80&w=1200", "content": "", "status": "PUBLISHED"}
        ]
        for item in updates:
            self._insert_missing("db_update", {"slug": item["slug"]}, item)
        # end for
        if self.mgdDB.db_gallery.find_one({"is_deleted": False}) == None:
            gallery = [
                {"image": "https://images.unsplash.com/photo-1529156069898-49953e654ee0?auto=format&fit=crop&q=80&w=900", "alt": "Alumni", "album": "Alumni", "order": 1, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&q=80&w=900", "alt": "Community", "album": "AHC 2027", "order": 2, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&q=80&w=900", "alt": "Events", "album": "Events", "order": 3, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=900", "alt": "Stage", "album": "Events", "order": 4, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1523050854058-8cb90180b9ae?auto=format&fit=crop&q=80&w=900", "alt": "University Fair", "album": "University Fair", "order": 5, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&q=80&w=900", "alt": "Workshop", "album": "Career Workshop", "order": 6, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?auto=format&fit=crop&q=80&w=900", "alt": "Preparation", "album": "Preparation", "order": 7, "status": "ENABLE"},
                {"image": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&q=80&w=900", "alt": "Behind the scenes", "album": "Behind The Scenes", "order": 8, "status": "ENABLE"}
            ]
            for item in gallery:
                self._insert("db_gallery", item)
            # end for
        # end if
        if self.mgdDB.db_timeline.find_one({"is_deleted": False}) == None:
            timeline = [
                {"month": "August 2026", "items": ["Finalization of PIC and division members"], "order": 1, "status": "ENABLE"},
                {"month": "September 2026", "items": ["Participant contribution", "Vendor listing", "Sponsorship listing"], "order": 2, "status": "ENABLE"},
                {"month": "October 2026", "items": ["Price comparison"], "order": 3, "status": "ENABLE"},
                {"month": "November 2026", "items": ["Officer visit", "SLAPUR survey", "Vendor survey"], "order": 4, "status": "ENABLE"},
                {"month": "December 2026", "items": ["Progress update"], "order": 5, "status": "ENABLE"},
                {"month": "March 2027", "items": ["Attendance confirmation", "AHC proposal presentation"], "order": 6, "status": "ENABLE"},
                {"month": "April 2027", "items": ["Finalization of member kits", "Gift purchases", "Other final preparations"], "order": 7, "status": "ENABLE"}
            ]
            for item in timeline:
                self._insert("db_timeline", item)
            # end for
        # end if
        if self.mgdDB.db_division.find_one({"is_deleted": False}) == None:
            names = [
                "Sponsorship", "Proposal Handler", "Merchandise", "University Fair",
                "FRACO Member Kit", "Career Workshop", "Gift Planner",
                "Social Media Admin", "Spiritual Affairs", "Event Vendor Handler"
            ]
            order = 1
            for name in names:
                self._insert("db_division", {"name": name, "order": order, "status": "ENABLE"})
                order = order + 1
            # end for
        # end if
        self.ensure_program_content()
        self.ensure_product_names()
        self.ensure_partner_content()
        self.ensure_update_content()
        self.ensure_admin_user()
        self.ensure_ops_admin_user()
        self.ensure_finance_user()
        self.ensure_officer_user()
        ahc_site_seed._did_seed = True
    # end def

    def ensure_program_content(self):
        details = {
            "university-fair": {
                "order": 1,
                "about": "University Fair connects students with universities and educational opportunities during FRACO's Alumni Home Coming 2027. Booths, conversations, and next-step guidance sit in one hall for the class of 2017 and the students around them.",
                "venue": "Venue to be announced",
                "venue_mode": "OFFLINE",
                "venue_url": "",
                "cta_label": "Register Your University",
                "cta_href": "/university-fair/register",
                "topics": [],
                "industries": []
            },
            "career-workshop": {
                "order": 2,
                "about": "Career Workshop is a practical track of speakers, industries, and sessions for alumni and students looking at the next step. Names and industries will be published as speakers confirm.",
                "venue": "Venue to be announced",
                "venue_mode": "HYBRID",
                "venue_url": "",
                "cta_label": "Register for Career Workshop",
                "cta_href": "/career-workshop/register",
                "topics": ["Industry talks", "CV and interview", "Building after campus", "Giving back through work"],
                "industries": ["To be announced"]
            },
            "spiritual-affairs": {
                "order": 3,
                "about": "Spiritual Affairs holds space in the FRACO calendar for gathering, vespers, and quiet. These activities are open to the class of 2017 and guests who want to take part.",
                "venue": "Venue to be announced",
                "venue_mode": "OFFLINE",
                "venue_url": "",
                "cta_label": "See Participate",
                "cta_href": "/participate",
                "topics": [],
                "industries": []
            },
            "events": {
                "order": 4,
                "about": "Events is the public listing for Alumni Home Coming 2027 — upcoming, open, closed, and completed. Register where a date is open, or follow Updates as the calendar fills.",
                "venue": "Venues listed per event",
                "venue_mode": "OFFLINE",
                "venue_url": "",
                "cta_label": "Register as Participant",
                "cta_href": "/participate",
                "topics": [],
                "industries": []
            }
        }
        for slug in details:
            self.mgdDB.db_program.update_one(
                {"slug": slug, "is_deleted": False},
                {"$set": details[slug]}
            )
        # end for
        faqs = [
            {"fk_program_slug": "university-fair", "question": "Who can register a booth?", "answer": "Universities and education partners can register a booth for University Fair through the form on this page.", "order": 1, "status": "ENABLE"},
            {"fk_program_slug": "university-fair", "question": "When is the listing confirmed?", "answer": "Participating universities appear here after FRACO confirms booth registration.", "order": 2, "status": "ENABLE"},
            {"fk_program_slug": "university-fair", "question": "Is there a fee?", "answer": "Booth terms will be shared after you register. Contribution details for participants stay on the Participate page.", "order": 3, "status": "ENABLE"},
            {"fk_program_slug": "career-workshop", "question": "Who can join?", "answer": "FRACO alumni from the class of 2017, students, and invited guests. Register to be notified when seats open.", "order": 1, "status": "ENABLE"},
            {"fk_program_slug": "career-workshop", "question": "When are speakers announced?", "answer": "Speaker cards go up as names are confirmed. Until then this page stays honest: to be announced.", "order": 2, "status": "ENABLE"},
            {"fk_program_slug": "spiritual-affairs", "question": "Do I need to register?", "answer": "Some gatherings are open walk-in. Use Participate if you want a reminder as dates lock in.", "order": 1, "status": "ENABLE"},
            {"fk_program_slug": "events", "question": "How do statuses work?", "answer": "Upcoming, Registration Open, Registration Closed, and Completed. Only open events take new registrations.", "order": 1, "status": "ENABLE"}
        ]
        for item in faqs:
            self._insert_missing("db_faq", {"fk_program_slug": item["fk_program_slug"], "question": item["question"]}, item)
        # end for
        schedules = [
            {"fk_program_slug": "university-fair", "title": "Booths open", "time_label": "Morning — to be announced", "order": 1, "status": "ENABLE"},
            {"fk_program_slug": "university-fair", "title": "Campus talks", "time_label": "Afternoon — to be announced", "order": 2, "status": "ENABLE"},
            {"fk_program_slug": "career-workshop", "title": "Opening and speakers", "time_label": "Morning — to be announced", "order": 1, "status": "ENABLE"},
            {"fk_program_slug": "career-workshop", "title": "Workshops", "time_label": "Afternoon — to be announced", "order": 2, "status": "ENABLE"}
        ]
        for item in schedules:
            self._insert_missing("db_schedule", {"fk_program_slug": item["fk_program_slug"], "title": item["title"]}, item)
        # end for
        if self.mgdDB.db_activity.find_one({"is_deleted": False}) == None:
            activities = [
                {"name": "Prayer Gathering", "date": "To be announced", "time_label": "Morning", "location": "To be announced", "description": "A shared opening for the FRACO calendar.", "status": "ENABLE"},
                {"name": "Wednesday Night", "date": "To be announced", "time_label": "Evening", "location": "To be announced", "description": "A midweek gathering during Alumni Home Coming 2027.", "status": "ENABLE"},
                {"name": "Vesper", "date": "To be announced", "time_label": "Evening", "location": "To be announced", "description": "Quiet space before the weekend program.", "status": "ENABLE"},
                {"name": "Fasting", "date": "To be announced", "time_label": "All day", "location": "To be announced", "description": "A spiritual activity held with the class of 2017.", "status": "ENABLE"}
            ]
            for item in activities:
                self._insert("db_activity", item)
            # end for
        # end if
        if self.mgdDB.db_event.find_one({"is_deleted": False}) == None:
            events = [
                {"title": "FRACO Opening Gathering", "date": "To be announced", "location": "To be announced", "description": "The public open of Alumni Home Coming 2027 for the class of 2017.", "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=1200", "event_status": "Upcoming", "status": "ENABLE"},
                {"title": "University Fair Day", "date": "To be announced", "location": "To be announced", "description": "Booths and campus talks. Universities register separately.", "image": "https://images.unsplash.com/photo-1523050854058-8cb90180b9ae?auto=format&fit=crop&q=80&w=1200", "event_status": "Registration Open", "status": "ENABLE"},
                {"title": "Career Workshop Day", "date": "To be announced", "location": "To be announced", "description": "Speakers and practical sessions. Register to hold a seat.", "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&q=80&w=1200", "event_status": "Registration Open", "status": "ENABLE"},
                {"title": "Preparation Briefing", "date": "December 2026", "location": "FRACO internal", "description": "An earlier briefing for division members. Registration is closed.", "image": "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?auto=format&fit=crop&q=80&w=1200", "event_status": "Registration Closed", "status": "ENABLE"}
            ]
            for item in events:
                self._insert("db_event", item)
            # end for
        # end if
    # end def

    def ensure_partner_content(self):
        packages = [
            {
                "slug": "package-a",
                "name": "Package A",
                "amount": "On request",
                "benefits": ["Lead partner mention across FRACO channels", "Priority logo on event materials", "Opening remarks opportunity"],
                "logo_placement": "Primary placement on stage, kits, and digital",
                "booth": "Premium booth if requested",
                "promo": "Hero mention in updates and social",
                "other": "Custom activations with the class of 2017",
                "order": 1,
                "status": "ENABLE"
            },
            {
                "slug": "package-b",
                "name": "Package B",
                "amount": "On request",
                "benefits": ["Supporting partner mention", "Logo on print and web", "Program-day presence"],
                "logo_placement": "Secondary placement on print and web",
                "booth": "Standard booth if requested",
                "promo": "Listing in partner updates",
                "other": "Shared photo and recap rights",
                "order": 2,
                "status": "ENABLE"
            },
            {
                "slug": "package-c",
                "name": "Package C",
                "amount": "On request",
                "benefits": ["Community partner listing", "Logo on the partners page", "Thank-you in the recap"],
                "logo_placement": "Partners page and recap materials",
                "booth": "Shared table if space allows",
                "promo": "Name listed with community partners",
                "other": "Invitation to Alumni Home Coming 2027 gatherings",
                "order": 3,
                "status": "ENABLE"
            },
            {
                "slug": "custom",
                "name": "Custom Partnership",
                "amount": "Custom",
                "benefits": ["Built with FRACO around your brief"],
                "logo_placement": "As agreed",
                "booth": "As agreed",
                "promo": "As agreed",
                "other": "In-kind, cash, or mixed support",
                "order": 4,
                "status": "ENABLE"
            }
        ]
        for item in packages:
            self._insert_missing("db_sponsor_package", {"slug": item["slug"]}, item)
        # end for
        categories = [
            "Catering", "Audio Visual", "Event Equipment", "Media",
            "Venue Support", "Decoration", "Transportation", "Other Event Services"
        ]
        order = 1
        for name in categories:
            self._insert_missing("db_vendor_category", {"name": name}, {
                "name": name,
                "order": order,
                "status": "ENABLE"
            })
            order = order + 1
        # end for
    # end def

    def ensure_update_content(self):
        articles = [
            {
                "slug": "registration-open",
                "title": "Participant contribution is open",
                "date": "1 September 2026",
                "category": "Announcements",
                "excerpt": "Join FRACO — class of 2017 — for Alumni Home Coming 2027. Full payment or installment from September through March.",
                "image": "https://images.unsplash.com/photo-1529156069898-49953e654ee0?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "Participant contribution for Alumni Home Coming 2027 is open. The amount is Rp 2.000.000 per person, with full payment or installments from September through March.\n\nRegister on the FRACO site, then wait for transfer details. FRACO does not take card payment on the site.\n\nThe Member Kit division prepares a tee, ID card, and lanyard for confirmed participants.",
                "status": "PUBLISHED"
            },
            {
                "slug": "vendor-listing",
                "title": "Vendor listing begins this month",
                "date": "3 September 2026",
                "category": "Event Updates",
                "excerpt": "Catering, AV, decoration, and support partners can apply now.",
                "image": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "The Event Vendor Handler division is opening the listing for Alumni Home Coming 2027. Catering, audio visual, decoration, transport, and other support partners can register on the vendors page.\n\nApplications are reviewed. Listing goes up after FRACO confirms.",
                "status": "PUBLISHED"
            },
            {
                "slug": "kit-preview",
                "title": "Member kit preview",
                "date": "5 September 2026",
                "category": "Behind the Scenes",
                "excerpt": "Tee, ID card, and lanyard — the kit the Member Kit division is building.",
                "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "The Member Kit division is building the kit for confirmed participants: a FRACO tee, ID card, and lanyard. Size is collected at registration. The kit is not sold in the merchandise store.",
                "status": "PUBLISHED"
            },
            {
                "slug": "calendar-live",
                "title": "The AHC 2027 calendar is live",
                "date": "8 September 2026",
                "category": "News",
                "excerpt": "August 2026 through April 2027 — the public timeline for the class of 2017.",
                "image": "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "The About page now carries the working calendar for Alumni Home Coming 2027: contribution and vendor listing in September, surveys later in the year, confirmation in March, and kits in April.\n\nDates can still move. FRACO will post here when a public day is locked.",
                "status": "PUBLISHED"
            },
            {
                "slug": "ten-years-on",
                "title": "Ten years on from 2017",
                "date": "10 September 2026",
                "category": "Throwback",
                "excerpt": "FRACO is the class of 2017. Alumni Home Coming 2027 is the gathering, not the graduation year.",
                "image": "https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "Graduation was 2017. The gathering is 2027. FRACO is the community in between — programs, merchandise, partners, and a place to come back.\n\nIf you have photos from the class years that you are willing to share, write to FRACO. We will not lift copyrighted pictures from other sites.",
                "status": "PUBLISHED"
            },
            {
                "slug": "how-to-take-part",
                "title": "How to take part",
                "date": "12 September 2026",
                "category": "Community",
                "excerpt": "Sponsor, vendor, university, or participant — four doors into AHC 2027.",
                "image": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&q=80&w=1200",
                "author": "FRACO",
                "content": "The Participate page is the conversion hub for Alumni Home Coming 2027. Companies apply as sponsors. Event businesses register as vendors. Universities book a University Fair booth. Alumni and guests register as participants.\n\nPick one track and FRACO will follow up.",
                "status": "PUBLISHED"
            }
        ]
        for item in articles:
            self._insert_missing("db_update", {"slug": item["slug"]}, item)
            self.mgdDB.db_update.update_one(
                {"slug": item["slug"], "is_deleted": False},
                {"$set": {
                    "author": item["author"],
                    "content": item["content"],
                    "category": item["category"],
                    "excerpt": item["excerpt"],
                    "title": item["title"]
                }}
            )
        # end for
    # end def

    def ensure_staff_account(self, email, password, name, role):
        email = (email or "").strip().lower()
        if email == "":
            return
        # end if
        existing = self.mgdDB.db_user.find_one({
            "email": email,
            "is_deleted": False
        })
        if existing != None:
            return
        # end if
        rec = database.new(self.mgdDB, "db_user")
        rec.put("fk_user_id", "")
        rec.put("username", email)
        rec.put("password", generate_password_hash(password))
        rec.put("role", role)
        rec.put("name", name)
        rec.put("phone", "")
        rec.put("email", email)
        rec.put("status", "ENABLE")
        rec.insert()
    # end def

    def ensure_admin_user(self):
        self.ensure_staff_account(
            config.G_ADMIN_EMAIL,
            config.G_ADMIN_PASSWORD,
            config.G_ADMIN_NAME,
            "SUPER_ADMIN"
        )
    # end def

    def ensure_ops_admin_user(self):
        self.ensure_staff_account(
            config.G_OPS_EMAIL,
            config.G_OPS_PASSWORD,
            config.G_OPS_NAME,
            "ADMIN"
        )
    # end def

    def ensure_finance_user(self):
        self.ensure_staff_account(
            config.G_FINANCE_EMAIL,
            config.G_FINANCE_PASSWORD,
            config.G_FINANCE_NAME,
            "FINANCE"
        )
    # end def

    def ensure_officer_user(self):
        self.ensure_staff_account(
            config.G_OFFICER_EMAIL,
            config.G_OFFICER_PASSWORD,
            config.G_OFFICER_NAME,
            "OFFICER"
        )
    # end def
# end class
