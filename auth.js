document.addEventListener('DOMContentLoaded', function() {
    const loginLink = document.getElementById('login-link');
    const signUpLinkNavItem = findSignUpLinkNavItem(); // Sign Up link is not always by id
    const logoutNavItem = document.getElementById('logout-item');
    const logoutLink = document.getElementById('logout-link');
    const adminNavItem = document.getElementById('admin-nav-item');

    // Function to find the Sign Up li.nav-item reliably
    function findSignUpLinkNavItem() {
        const navItems = document.querySelectorAll('nav .nav-items .nav-item a');
        for (let item of navItems) {
            if (item.href && item.href.includes('signUp.html')) {
                return item.closest('.nav-item'); // Get the parent <li> element
            }
        }
        return null;
    }

    function updateNavbar() {
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        const userType = localStorage.getItem('userType');

        if (isLoggedIn === 'true') {
            if (loginLink && loginLink.closest('.nav-item')) {
                loginLink.closest('.nav-item').style.display = 'none';
            }
            if (signUpLinkNavItem) {
                signUpLinkNavItem.style.display = 'none';
            }
            if (logoutNavItem) {
                logoutNavItem.style.display = 'list-item'; // Or 'block' if it's not a list item directly
            }
            if (adminNavItem) {
                if (userType === 'admin') {
                    adminNavItem.style.display = 'block';
                } else {
                    adminNavItem.style.display = 'none';
                }
            }
        } else {
            if (loginLink && loginLink.closest('.nav-item')) {
                loginLink.closest('.nav-item').style.display = 'list-item';
            }
            if (signUpLinkNavItem) {
                signUpLinkNavItem.style.display = 'list-item';
            }
            if (logoutNavItem) {
                logoutNavItem.style.display = 'none';
            }
            if (adminNavItem) {
                adminNavItem.style.display = 'none';
            }
        }
    }

    if (logoutLink) {
        logoutLink.addEventListener('click', function(event) {
            event.preventDefault();
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('username');
            localStorage.removeItem('email');
            localStorage.removeItem('userType');
            
            updateNavbar(); // Update navbar immediately
            
            // Redirect to login page after logout
            window.location.href = 'login.html'; 
        });
    }

    // Initial call to set navbar state on page load
    updateNavbar();
}); 