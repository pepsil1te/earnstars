let tg = window.Telegram.WebApp;
tg.expand();

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    // Установка данных пользователя
    if (tg.initDataUnsafe.user) {
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.textContent = '@' + tg.initDataUnsafe.user.username;
        }
        const avatarElement = document.getElementById('userAvatar');
        if (avatarElement) {
            if (tg.initDataUnsafe.user.photo_url) {
                avatarElement.style.backgroundImage = `url(${tg.initDataUnsafe.user.photo_url})`;
            } else {
                avatarElement.textContent = tg.initDataUnsafe.user.first_name.charAt(0).toUpperCase();
            }
        }
    }

    // Добавляем обработчик для переключения языка
    const languageSelector = document.querySelector('.language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('click', toggleLanguage);
    }

    // Инициализация анимаций
    initAnimations();

    // Инициализация реферальной системы
    initReferralSystem();

    // Показываем главную страницу по умолчанию
    const mainPage = document.getElementById('main-page');
    if (mainPage) {
        mainPage.classList.add('active');
    }
    const premiumModal = document.getElementById('premium-modal');
    if (premiumModal) {
        premiumModal.style.display = 'none';
    }
    
    loadPrices();
});

// Инициализация анимаций
function initAnimations() {
    // Инициализация анимаций подарков
    const giftAnimations = {
        'heart': 'gifts/heart.json',
        'bear': 'gifts/bear.json',
        'present': 'gifts/present.json',
        'ring': 'gifts/ring.json'
    };

    Object.entries(giftAnimations).forEach(([id, path]) => {
        const container = document.getElementById(`${id}-animation`);
        if (container) {
            lottie.loadAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: path
            });
        }
    });
}

// Навигация
function navigate(page) {
    const currentPage = document.querySelector('.page.active');
    const targetPage = document.getElementById(page + '-page');
    
    // Если уходим со страницы покупки звезд, сворачиваем пакеты
    if (currentPage && currentPage.id === 'buy-page' && targetPage.id !== 'buy-page') {
        const packagesContainer = document.querySelector('.packages');
        if (packagesContainer && packagesExpanded) {
            packagesExpanded = true; // Устанавливаем true, чтобы следующий вызов showAllPackages свернул пакеты
            showAllPackages();
        }
    }
    
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.getAttribute('onclick').includes(page));
    });
}

// Переключение языка
let currentLanguage = 'ru';

function toggleLanguage() {
    currentLanguage = currentLanguage === 'ru' ? 'en' : 'ru';
    const currentLangElement = document.getElementById('currentLang');
    if (currentLangElement) {
        currentLangElement.textContent = currentLanguage.toUpperCase();
    }
    updateTexts();
}

function updateTexts() {
    document.querySelectorAll('.lang-text').forEach(element => {
        const text = element.getAttribute(`data-${currentLanguage}`);
        if (text) element.textContent = text;
    });
}

// Функции для покупки звезд
function buyForSelf() {
    if (tg.initDataUnsafe.user && tg.initDataUnsafe.user.username) {
        const recipientInput = document.getElementById('recipient');
        if (recipientInput) {
            recipientInput.value = '@' + tg.initDataUnsafe.user.username;
            recipientInput.classList.remove('error-field');
            const errorMsg = document.getElementById('recipient-error');
            if (errorMsg) errorMsg.remove();
        }
    } else {
        const recipientInput = document.getElementById('recipient');
        if (recipientInput) {
            recipientInput.classList.add('error-field');
            const existingError = document.getElementById('recipient-error');
            if (!existingError) {
                const errorMsg = document.createElement('div');
                errorMsg.id = 'recipient-error';
                errorMsg.className = 'error-message';
                errorMsg.textContent = currentLanguage === 'ru' ? 'Username не определен' : 'Username not found';
                const parentNode = recipientInput.parentNode;
                if (parentNode) {
                    parentNode.appendChild(errorMsg);
                }
            }
        }
    }
}

function buyStars() {
    navigate('buy');
    packagesExpanded = false;
    const packagesContainer = document.querySelector('.packages');
    if (packagesContainer) {
        const packagesHtml = allPackages.slice(0, 4).map(pkg => `
            <div class="package" onclick="selectPackage(${pkg.stars})">
                <div class="package-stars">
                    <img src="svg/star.svg" alt="star" class="star-icon">
                    <span>${pkg.stars.toLocaleString()} звёзд</span>
                </div>
                <div class="package-price">${pkg.price} ₽ <span class="usd">~${pkg.usd} $</span></div>
            </div>
        `).join('');
        packagesContainer.innerHTML = packagesHtml;
    }
    const button = document.querySelector('.show-more');
    if (button) {
        button.textContent = currentLanguage === 'ru' ? 'Показать все пакеты' : 'Show all packages';
    }
    const starsPayButton = document.getElementById('stars-pay-button');
    if (starsPayButton) {
        starsPayButton.style.display = 'none';
    }
}

function selectPackage(amount) {
    selectedPackage = allPackages.find(pkg => pkg.stars === amount);
    const packages = document.querySelectorAll('.package');
    packages.forEach(pkg => pkg.classList.remove('selected'));
    
    const selectedElement = document.querySelector(`.package[onclick="selectPackage(${amount})"]`);
    if (selectedElement) {
        selectedElement.classList.add('selected');
    }
    
    const payButton = document.getElementById('stars-pay-button');
    if (payButton) {
        payButton.style.display = 'block';
        const packagesSection = document.querySelector('.packages-section');
        if (packagesSection) {
            const packagesBottom = packagesSection.getBoundingClientRect().bottom;
            const windowHeight = window.innerHeight;
            const bottomOffset = windowHeight - packagesBottom;
            if (bottomOffset < 160) { // Если пакеты занимают много места
                payButton.style.position = 'relative';
                payButton.style.bottom = 'auto';
                payButton.style.marginTop = '20px';
            } else {
                payButton.style.position = 'fixed';
                payButton.style.bottom = '80px';
                payButton.style.marginTop = '0';
            }
        }
    }
}

let packagesExpanded = false;

function showAllPackages() {
    const packagesContainer = document.querySelector('.packages');
    if (!packagesContainer) return;
    
    const button = document.querySelector('.show-more');
    if (!button) return;
    
    packagesExpanded = !packagesExpanded;
    
    if (packagesExpanded) {
        const packagesHtml = allPackages.map(pkg => `
            <div class="package" onclick="selectPackage(${pkg.stars})">
                <div class="package-stars">
                    <img src="svg/star.svg" alt="star" class="star-icon">
                    <span>${pkg.stars.toLocaleString()} звёзд</span>
                </div>
                <div class="package-price">${pkg.price} ₽ <span class="usd">~${pkg.usd} $</span></div>
            </div>
        `).join('');
        
        packagesContainer.innerHTML = packagesHtml;
        button.textContent = currentLanguage === 'ru' ? 'Скрыть пакеты' : 'Hide packages';
        packagesContainer.style.maxHeight = 'none';
    } else {
        const packagesHtml = allPackages.slice(0, 4).map(pkg => `
            <div class="package" onclick="selectPackage(${pkg.stars})">
                <div class="package-stars">
                    <img src="svg/star.svg" alt="star" class="star-icon">
                    <span>${pkg.stars.toLocaleString()} звёзд</span>
                </div>
                <div class="package-price">${pkg.price} ₽ <span class="usd">~${pkg.usd} $</span></div>
            </div>
        `).join('');
        
        packagesContainer.innerHTML = packagesHtml;
        button.textContent = currentLanguage === 'ru' ? 'Показать все пакеты' : 'Show all packages';
        packagesContainer.style.maxHeight = '';
    }
}

async function checkCurrentPrice() {
    try {
        // Проверяем, запущено ли приложение на GitHub Pages
        const isGitHubPages = window.location.hostname.includes('github.io');
        const response = await fetch(isGitHubPages ? 'prices.json' : '/prices');
        const prices = await response.json();
        const currentPackage = prices.stars.packages.find(p => p.stars === selectedPackage.stars);
        
        if (currentPackage.price !== selectedPackage.price) {
            tg.showPopup({
                title: 'Цена изменилась',
                message: `Цена на пакет ${selectedPackage.stars} звезд изменилась с ${selectedPackage.price}₽ на ${currentPackage.price}₽. Пожалуйста, выберите пакет заново.`,
                buttons: [{text: 'OK', type: 'ok'}]
            });
            allPackages = prices.stars.packages;
            showAllPackages();
            return false;
        }
        return true;
    } catch (error) {
        console.error('Error checking price:', error);
        return false;
    }
}

async function processStarsPayment() {
    if (!selectedPackage) {
        tg.showPopup({
            title: 'Ошибка',
            message: 'Пожалуйста, выберите пакет звезд',
            buttons: [{text: 'OK', type: 'ok'}]
        });
        return;
    }

    // Проверяем актуальность цены перед оплатой
    const priceIsValid = await checkCurrentPrice();
    if (!priceIsValid) {
        return;
    }

    const recipient = document.getElementById('recipient').value.trim();
    const email = document.getElementById('email').value.trim();
    const starsAmount = document.getElementById('starsAmount').value;
    
    let hasError = false;
    
    // Валидация получателя
    if (!recipient) {
        const recipientInput = document.getElementById('recipient');
        recipientInput.classList.add('error-field');
        const existingError = document.getElementById('recipient-error');
        if (!existingError) {
            const errorMsg = document.createElement('div');
            errorMsg.id = 'recipient-error';
            errorMsg.className = 'error-message';
            errorMsg.textContent = currentLanguage === 'ru' ? 'Введите получателя' : 'Enter recipient';
            const parentNode = recipientInput.parentNode;
            if (parentNode) {
                parentNode.appendChild(errorMsg);
            }
        }
        hasError = true;
    }
    
    // Валидация email
    if (!email || !email.includes('@')) {
        const emailInput = document.getElementById('email');
        emailInput.classList.add('error-field');
        const existingError = document.getElementById('email-error');
        if (!existingError) {
            const errorMsg = document.createElement('div');
            errorMsg.id = 'email-error';
            errorMsg.className = 'error-message';
            errorMsg.textContent = currentLanguage === 'ru' ? 'Введите корректный email' : 'Enter valid email';
            emailInput.parentNode.appendChild(errorMsg);
        }
        hasError = true;
    }
    
    // Валидация количества звезд
    if (!starsAmount || starsAmount < 50 || starsAmount > 20000) {
        const starsInput = document.getElementById('starsAmount');
        starsInput.classList.add('error-field');
        const existingError = document.getElementById('stars-error');
        if (!existingError) {
            const errorMsg = document.createElement('div');
            errorMsg.id = 'stars-error';
            errorMsg.className = 'error-message';
            errorMsg.textContent = currentLanguage === 'ru' ? 'Введите количество от 50 до 20 000' : 'Enter amount between 50 and 20,000';
            starsInput.parentNode.appendChild(errorMsg);
        }
        hasError = true;
    }
    
    if (!hasError) {
        // Отправляем данные на сервер или в Telegram Web App
        tg.MainButton.text = currentLanguage === 'ru' ? 'ОПЛАТИТЬ' : 'PAY';
        tg.MainButton.show();
        tg.MainButton.onClick(() => {
            tg.sendData(JSON.stringify({
                action: 'buy_stars',
                recipient: recipient,
                email: email,
                amount: parseInt(starsAmount)
            }));
        });
    }
}

// Обработчики модальных окон
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.classList.add('active');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
    }
}

function buyPremium() {
    const modal = document.getElementById('premium-modal');
    if (modal) {
        modal.style.display = 'block';
        modal.style.animation = 'slideIn 0.3s ease-out forwards';
    }
    if (tg.initDataUnsafe.user) {
        const premiumRecipientElement = document.getElementById('premium-recipient');
        if (premiumRecipientElement) {
            premiumRecipientElement.value = '@' + tg.initDataUnsafe.user.username;
        }
    }
}

function hidePremiumModal() {
    const modal = document.getElementById('premium-modal');
    if (modal) {
        modal.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
    const premiumPayButton = document.getElementById('premium-pay-button');
    if (premiumPayButton) {
        premiumPayButton.style.display = 'none';
    }
    selectedPremiumPackage = null;
    document.querySelectorAll('.premium-package').forEach(pkg => pkg.classList.remove('selected'));
}

function showGiftModal(giftType, price) {
    const modal = document.getElementById('gift-modal');
    if (modal) {
        modal.classList.add('active');
    }
    const preview = document.getElementById('gift-preview');
    if (preview) {
        // Очищаем предыдущую анимацию
        preview.innerHTML = '';
        
        // Создаем новую анимацию для превью
        lottie.loadAnimation({
            container: preview,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: `gifts/${giftType}.json`
        });
    }
    currentGift = { type: giftType, price: price };
    
    // Автозаполнение получателя
    if (tg.initDataUnsafe.user) {
        const giftRecipientElement = document.getElementById('gift-recipient');
        if (giftRecipientElement) {
            giftRecipientElement.value = '@' + tg.initDataUnsafe.user.username;
        }
    }
}

function hideGiftModal() {
    const modal = document.getElementById('gift-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    const preview = document.getElementById('gift-preview');
    if (preview) {
        preview.innerHTML = '';
    }
    currentGift = null;
}

function updateCharCounter(textarea) {
    const counter = document.getElementById('char-count');
    if (counter) {
        counter.textContent = textarea.value.length;
    }
}

function processGiftPayment() {
    if (!currentGift) return;

    const recipient = document.getElementById('gift-recipient').value;
    const email = document.getElementById('gift-email').value;
    const message = document.getElementById('gift-message').value;

    if (!recipient || !email) {
        tg.showAlert('Пожалуйста, заполните все обязательные поля');
        return;
    }

    // Здесь будет логика оплаты
    tg.showAlert(`Покупка подарка ${currentGift.type} для ${recipient}\nСумма: ${currentGift.price} звезд`);
    hideGiftModal();
}

function buyGift() {
    navigate('gifts');
}

function selectGift(type) {
    tg.showConfirm('Купить подарок?', (confirmed) => {
        if (confirmed) {
            tg.showAlert('Функция покупки подарков скоро будет доступна!');
        }
    });
}

// Функции для Premium
let selectedPremiumPackage = null;

function selectPremiumPackage(element, duration, price) {
    document.querySelectorAll('.premium-package').forEach(pkg => pkg.classList.remove('selected'));
    if (element) {
        element.classList.add('selected');
    }
    selectedPremiumPackage = { duration, price };
    const premiumPayButton = document.getElementById('premium-pay-button');
    if (premiumPayButton) {
        premiumPayButton.style.display = 'block';
    }
}

function processPremiumPayment() {
    if (!selectedPremiumPackage) return;

    const recipient = document.getElementById('premium-recipient').value;
    const email = document.getElementById('premium-email').value;

    if (!recipient || !email) {
        tg.showAlert('Пожалуйста, заполните все обязательные поля');
        return;
    }

    // Здесь будет логика оплаты
    tg.showAlert(`Покупка Premium на ${selectedPremiumPackage.duration} мес.\nДля: ${recipient}\nСумма: ${selectedPremiumPackage.price} ₽`);
    hidePremiumModal();
}

// Функции для заработка
function withdrawStars() {
    tg.showAlert('Функция вывода звезд скоро будет доступна!');
}

function showReferrals() {
    tg.showAlert('Функция просмотра рефералов скоро будет доступна!');
}

function showReferralTransactions() {
    tg.showAlert('Функция просмотра операций рефералов скоро будет доступна!');
}

// Функции для транзакций
function showTransactions() {
    navigate('transactions');
}

// Дополнительные функции
function subscribeChannel() {
    window.open('https://t.me/ez_stars', '_blank');
}

function contactSupport() {
    window.open('https://t.me/ooostyx', '_blank');
}

let allPackages = [];
let selectedPackage = null;

// Функция для загрузки актуальных цен
async function loadPrices() {
    try {
        // Проверяем, запущено ли приложение на GitHub Pages
        const isGitHubPages = window.location.hostname.includes('github.io');
        const response = await fetch(isGitHubPages ? 'prices.json' : '/prices');
        const prices = await response.json();
        allPackages = prices.stars.packages;
        showAllPackages();
    } catch (error) {
        console.error('Error loading prices:', error);
    }
}

// Реферальная система
function initReferralSystem() {
    if (tg.initDataUnsafe.user) {
        const userId = tg.initDataUnsafe.user.id;
        const referralLink = `https://t.me/EarnStarsBot?start=ref${userId}`;
        
        // Загружаем статистику из localStorage
        const referralStats = {
            count: parseInt(localStorage.getItem('referralCount') || '0'),
            stars: parseInt(localStorage.getItem('referralStars') || '0')
        };
        
        updateReferralStats(referralStats);
    }
}

function updateReferralStats(stats) {
    const referralCountElement = document.getElementById('referralCount');
    if (referralCountElement) {
        referralCountElement.textContent = stats.count;
    }
    const referralStarsElement = document.getElementById('referralStars');
    if (referralStarsElement) {
        referralStarsElement.textContent = `${stats.stars} ⭐`;
    }
}

function copyReferralLink() {
    if (tg.initDataUnsafe.user) {
        const userId = tg.initDataUnsafe.user.id;
        const referralLink = `https://t.me/EarnStarsBot?start=ref${userId}`;
        
        navigator.clipboard.writeText(referralLink)
            .then(() => {
                tg.showPopup({
                    title: 'Успешно!',
                    message: 'Реферальная ссылка скопирована в буфер обмена'
                });
            })
            .catch(() => {
                tg.showPopup({
                    title: 'Ошибка',
                    message: 'Не удалось скопировать ссылку'
                });
            });
    }
}

function inviteFriends() {
    if (tg.initDataUnsafe.user) {
        const userId = tg.initDataUnsafe.user.id;
        const referralLink = `https://t.me/EarnStarsBot?start=ref${userId}`;
        tg.shareUrl(referralLink);
    }
}

let currentGift = null;
