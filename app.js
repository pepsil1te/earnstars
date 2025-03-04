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
});

// Инициализация анимаций
function initAnimations() {
    const animations = {
        'heart': document.getElementById('heart-animation'),
        'bear': document.getElementById('bear-animation')
    };

    for (let [name, container] of Object.entries(animations)) {
        if (container) {
            lottie.loadAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: `gifts/${name}.json`
            });
        }
    }
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
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.value = '@' + tg.initDataUnsafe.user.username;
            usernameElement.classList.remove('error-field');
            const errorMsg = document.getElementById('username-error');
            if (errorMsg) errorMsg.remove();
        }
    } else {
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.classList.add('error-field');
            const existingError = document.getElementById('username-error');
            if (!existingError) {
                const errorMsg = document.createElement('div');
                errorMsg.id = 'username-error';
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Username не определен';
                const parentNode = usernameElement.parentNode;
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
    showAllPackages();
    const starsPayButton = document.getElementById('stars-pay-button');
    if (starsPayButton) {
        starsPayButton.style.display = 'none';
    }
}

function selectPackage(amount) {
    const starsAmountElement = document.getElementById('starsAmount');
    if (starsAmountElement) {
        starsAmountElement.value = amount;
    }
    const payButton = document.getElementById('stars-pay-button');
    if (payButton) {
        payButton.style.display = 'block';
        
        // Учитываем состояние списка пакетов для позиционирования кнопки
        const packagesWrapper = document.querySelector('.packages-wrapper');
        if (packagesWrapper) {
            if (packagesExpanded) {
                packagesWrapper.classList.add('expanded');
            } else {
                packagesWrapper.classList.remove('expanded');
            }
        }
    }
}

function showAllPackages() {
    const packagesContainer = document.querySelector('.packages');
    if (!packagesContainer) return;
    
    const packagesWrapper = document.querySelector('.packages-wrapper');
    const button = document.querySelector('.show-more');
    if (!button) return;
    
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
        button.textContent = 'Скрыть пакеты';
        if (packagesWrapper) {
            packagesWrapper.classList.add('expanded');
        }
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
        button.textContent = 'Показать все пакеты';
        if (packagesWrapper) {
            packagesWrapper.classList.remove('expanded');
        }
    }
    
    packagesExpanded = !packagesExpanded;
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

const allPackages = [
    { stars: 50, price: 50, usd: 0.75 },
    { stars: 75, price: 75, usd: 1.13 },
    { stars: 100, price: 100, usd: 1.50 },
    { stars: 150, price: 150, usd: 2.25 },
    { stars: 250, price: 250, usd: 3.75 },
    { stars: 350, price: 350, usd: 5.25 },
    { stars: 500, price: 500, usd: 7.50 },
    { stars: 750, price: 750, usd: 11.25 },
    { stars: 1000, price: 1000, usd: 15 },
    { stars: 1500, price: 1500, usd: 22.50 },
    { stars: 2500, price: 2500, usd: 37.50 },
    { stars: 5000, price: 5000, usd: 75 },
    { stars: 10000, price: 10000, usd: 150 },
    { stars: 25000, price: 25000, usd: 375 },
    { stars: 35000, price: 35000, usd: 525 },
    { stars: 50000, price: 50000, usd: 750 }
];

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
