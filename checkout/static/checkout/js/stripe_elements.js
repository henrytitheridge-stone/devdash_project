/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Extract Stripe keys from the template variables
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

// Custom styling for the Stripe card element
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

// Create and mount the Stripe card element
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';        
    }
});

// Handle form submission
var form = document.getElementById('payment-form')

form.addEventListener('submit', function(ev) {
    ev.preventDefault();

    // Disable card input and submit button to prevent multiple charges
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
 
    // Prepare data to send to the cache_checkout_data view
    var postData = {
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
        'client_secret': clientSecret,
    };

    var url = '/checkout/cache_checkout_data/';

    // Update the payment intent metadata
    $.post(url, postData).done(function () {

        // And confirm the payment with Stripe
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                }
            }
        }).then(function(result){
            if (result.error) {

                // If Stripe returns an error, re-enable form for user to fix
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {

                // If payment succeeds, submit hidden form to create order
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {

        // If the initial post fails, reload the page
        location.reload();
    })
});
