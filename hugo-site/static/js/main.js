/**
 * İsim Sözlüğü - Ana JavaScript Dosyası
 * Bebek İsimleri ve Anlamları
 */

// ----------------------------------------
// Arama İndeksi
// ----------------------------------------
let searchIndex = [];
let searchIndexLoaded = false;

async function loadSearchIndex() {
    if (searchIndexLoaded) return;

    try {
        const response = await fetch('/index.json');
        if (response.ok) {
            searchIndex = await response.json();
            searchIndexLoaded = true;
        }
    } catch (error) {
        console.error('Arama indeksi yüklenemedi:', error);
    }
}

// Türkçe karakter normalizasyonu
function normalizeText(text) {
    if (!text) return '';
    return text
        .toLowerCase()
        .replace(/ı/g, 'i')
        .replace(/ğ/g, 'g')
        .replace(/ü/g, 'u')
        .replace(/ş/g, 's')
        .replace(/ö/g, 'o')
        .replace(/ç/g, 'c')
        .replace(/İ/g, 'i')
        .replace(/Ğ/g, 'g')
        .replace(/Ü/g, 'u')
        .replace(/Ş/g, 's')
        .replace(/Ö/g, 'o')
        .replace(/Ç/g, 'c');
}

// İçerik arama
function searchContent(query) {
    if (!query || query.length < 2) return [];

    const normalizedQuery = normalizeText(query);

    const results = searchIndex
        .filter(item => {
            const normalizedTitle = normalizeText(item.title);
            const normalizedContent = normalizeText(item.content || '');
            return normalizedTitle.includes(normalizedQuery) ||
                   normalizedContent.includes(normalizedQuery);
        })
        .map(item => {
            const normalizedTitle = normalizeText(item.title);
            const priority = normalizedTitle.startsWith(normalizedQuery) ? 0 :
                           normalizedTitle.includes(normalizedQuery) ? 1 : 2;
            return { ...item, priority };
        })
        .sort((a, b) => a.priority - b.priority)
        .slice(0, 10);

    return results;
}

// Arama sonuçlarını render et
function renderSearchResults(results, container) {
    if (!container) return;

    if (results.length === 0) {
        container.innerHTML = '<div class="search-no-results">Sonuç bulunamadı</div>';
        container.classList.add('active');
        return;
    }

    const html = results.map(item => `
        <a href="${item.permalink}" class="search-result-item">
            <div class="search-result-title">${item.title}</div>
            ${item.cinsiyet ? `<span class="search-result-gender ${item.cinsiyet}">${item.cinsiyet === 'erkek' ? '👦' : '👧'}</span>` : ''}
        </a>
    `).join('');

    container.innerHTML = html;
    container.classList.add('active');
}

// ----------------------------------------
// Event Listeners
// ----------------------------------------
document.addEventListener('DOMContentLoaded', function() {
    // Arama indeksini yükle
    loadSearchIndex();

    // Header Arama
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    const results = searchContent(query);
                    renderSearchResults(results, searchResults);
                } else {
                    searchResults.classList.remove('active');
                }
            }, 200);
        });

        searchInput.addEventListener('focus', function() {
            if (this.value.length >= 2) {
                searchResults.classList.add('active');
            }
        });

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });
    }

    // Hero Arama
    const heroSearchInput = document.getElementById('hero-search-input');
    const heroSearchResults = document.getElementById('hero-search-results');
    const heroSearchBtn = document.getElementById('hero-search-btn');

    if (heroSearchInput && heroSearchResults) {
        let debounceTimer;

        heroSearchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    const results = searchContent(query);
                    renderSearchResults(results, heroSearchResults);
                } else {
                    heroSearchResults.classList.remove('active');
                }
            }, 200);
        });

        heroSearchInput.addEventListener('focus', function() {
            if (this.value.length >= 2) {
                heroSearchResults.classList.add('active');
            }
        });

        document.addEventListener('click', function(e) {
            if (!heroSearchInput.contains(e.target) && !heroSearchResults.contains(e.target)) {
                heroSearchResults.classList.remove('active');
            }
        });

        if (heroSearchBtn) {
            heroSearchBtn.addEventListener('click', function() {
                const query = heroSearchInput.value.trim();
                if (query.length >= 2) {
                    const results = searchContent(query);
                    if (results.length > 0) {
                        window.location.href = results[0].permalink;
                    }
                }
            });
        }

        heroSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query.length >= 2) {
                    const results = searchContent(query);
                    if (results.length > 0) {
                        window.location.href = results[0].permalink;
                    }
                }
            }
        });
    }

    // Mobile Menu
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Back to Top
    const backToTop = document.getElementById('back-to-top');

    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });

        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// ----------------------------------------
// JSON Search Index Output Template
// ----------------------------------------
// Bu dosya hugo-site/layouts/index.json olarak kaydedilmeli
/*
{{- $.Scratch.Add "index" slice -}}
{{- range where .Site.RegularPages "Section" "isim" -}}
    {{- $.Scratch.Add "index" (dict "title" .Title "permalink" .Permalink "content" .Plain "cinsiyet" .Params.cinsiyet "koken" .Params.koken) -}}
{{- end -}}
{{- $.Scratch.Get "index" | jsonify -}}
*/
