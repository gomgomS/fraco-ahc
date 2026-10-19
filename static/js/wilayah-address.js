(function () {
    var BASE = "/api/wilayah";

    function text(el) {
        return (el && el.value ? String(el.value) : "").trim();
    }

    function setOptions(select, items, placeholder, selected) {
        if (!select) return;
        var keep = selected || "";
        select.innerHTML = "";
        var first = document.createElement("option");
        first.value = "";
        first.textContent = placeholder;
        select.appendChild(first);
        (items || []).forEach(function (item) {
            var opt = document.createElement("option");
            opt.value = item.id || "";
            opt.textContent = item.name || "";
            if (item.postal_code) opt.setAttribute("data-postal", item.postal_code);
            if (keep && String(item.id) === String(keep)) opt.selected = true;
            select.appendChild(opt);
        });
        select.disabled = false;
    }

    function fetchList(path) {
        return fetch(BASE + "/" + path, { credentials: "same-origin" })
            .then(function (resp) { return resp.json(); })
            .then(function (payload) { return payload && payload.data ? payload.data : []; })
            .catch(function () { return []; });
    }

    function selectedName(select) {
        if (!select || !select.selectedOptions || !select.selectedOptions[0]) return "";
        return (select.selectedOptions[0].textContent || "").trim();
    }

    function selectedPostal(select) {
        if (!select || !select.selectedOptions || !select.selectedOptions[0]) return "";
        return select.selectedOptions[0].getAttribute("data-postal") || "";
    }

    function initRoot(root) {
        if (!root || root.getAttribute("data-wilayah-ready") === "1") return;
        root.setAttribute("data-wilayah-ready", "1");
        var province = root.querySelector('[data-wilayah="province"]');
        var city = root.querySelector('[data-wilayah="city"]');
        var district = root.querySelector('[data-wilayah="district"]');
        var village = root.querySelector('[data-wilayah="village"]');
        var postal = root.querySelector('[data-wilayah="postal"]');
        var nameProvince = root.querySelector('[data-wilayah-name="province"]');
        var nameCity = root.querySelector('[data-wilayah-name="city"]');
        var nameDistrict = root.querySelector('[data-wilayah-name="district"]');
        var nameVillage = root.querySelector('[data-wilayah-name="village"]');
        if (!province || !city || !district || !village) return;

        function syncNames() {
            if (nameProvince) nameProvince.value = selectedName(province);
            if (nameCity) nameCity.value = selectedName(city);
            if (nameDistrict) nameDistrict.value = selectedName(district);
            if (nameVillage) nameVillage.value = selectedName(village);
        }

        function resetAfter(level) {
            var chain = [
                { el: city, placeholder: "Pilih kabupaten / kota" },
                { el: district, placeholder: "Pilih kecamatan" },
                { el: village, placeholder: "Pilih kelurahan / desa" }
            ];
            chain.forEach(function (item, idx) {
                if (idx < level) return;
                setOptions(item.el, [], item.placeholder, "");
                item.el.disabled = true;
            });
            if (level <= 2 && postal && postal.getAttribute("data-autofill") !== "no") {
                postal.value = "";
            }
        }

        function loadCities(selected) {
            var id = text(province);
            if (!id) {
                resetAfter(0);
                syncNames();
                return Promise.resolve();
            }
            city.disabled = true;
            return fetchList("regencies/" + encodeURIComponent(id) + ".json").then(function (items) {
                setOptions(city, items, "Pilih kabupaten / kota", selected);
                if (!selected) resetAfter(1);
                syncNames();
            });
        }

        function loadDistricts(selected) {
            var id = text(city);
            if (!id) {
                resetAfter(1);
                syncNames();
                return Promise.resolve();
            }
            district.disabled = true;
            return fetchList("districts/" + encodeURIComponent(id) + ".json").then(function (items) {
                setOptions(district, items, "Pilih kecamatan", selected);
                if (!selected) resetAfter(2);
                syncNames();
            });
        }

        function loadVillages(selected) {
            var id = text(district);
            if (!id) {
                resetAfter(2);
                syncNames();
                return Promise.resolve();
            }
            village.disabled = true;
            return fetchList("villages/" + encodeURIComponent(id) + ".json").then(function (items) {
                setOptions(village, items, "Pilih kelurahan / desa", selected);
                if (selected) {
                    var code = selectedPostal(village);
                    if (code && postal) postal.value = code;
                } else if (postal && postal.getAttribute("data-autofill") !== "no") {
                    postal.value = "";
                }
                syncNames();
            });
        }

        province.addEventListener("change", function () {
            resetAfter(0);
            loadCities("");
            syncNames();
        });
        city.addEventListener("change", function () {
            resetAfter(1);
            loadDistricts("");
            syncNames();
        });
        district.addEventListener("change", function () {
            resetAfter(2);
            loadVillages("");
            syncNames();
        });
        village.addEventListener("change", function () {
            var code = selectedPostal(village);
            if (code && postal) postal.value = code;
            syncNames();
        });

        fetchList("provinces.json").then(function (items) {
            setOptions(province, items, "Pilih provinsi", province.getAttribute("data-selected") || "");
            var cityId = city.getAttribute("data-selected") || "";
            var districtId = district.getAttribute("data-selected") || "";
            var villageId = village.getAttribute("data-selected") || "";
            return loadCities(cityId).then(function () {
                return loadDistricts(districtId);
            }).then(function () {
                return loadVillages(villageId);
            });
        });
    }

    function initAll() {
        var roots = document.querySelectorAll("[data-address-root]");
        for (var i = 0; i < roots.length; i += 1) initRoot(roots[i]);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAll);
    } else {
        initAll();
    }
    window.initWilayahAddress = initAll;
})();
