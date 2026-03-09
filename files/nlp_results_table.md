# NLP Method Comparison – Action & Target per Step

Each cell shows `Action`: target(s).  Multi-pair steps use ➜ as separator.
✓ = action correct AND all targets match.  ✗ = mismatch.

---

## App1-TestCase1.feature
**Test Case 1: Verify Subscription in home page**  
URLs: http://automationexercise.com

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Scroll down to footer | `Scroll`: footer | ✓ `Scroll`: footer | ✓ `Scroll`: footer | ✗ `footer`: — | ✗ `footer`: — | ✓ `Scroll`: footer | ✓ `Scroll`: footer |
| 5 | Verify text 'SUBSCRIPTION' | `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✗ `—`: — | ✗ `—`: — | ✓ `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION |
| 6 | Enter email address in input and click arrow button | `Enter`: email address ➜ `Click`: arrow button | ✓ `Enter`: email address in input ➜ `click`: arrow button | ✓ `Enter`: email address ➜ `click`: arrow button | ✗ `—`: — ➜ `—`: — | ✗ `—`: — ➜ `—`: — | ✓ `Enter`: email address ➜ `click`: arrow button | ✓ `Enter`: email address ➜ `click`: arrow button |
| 7 | Verify success message 'You have been successfully subscribed!' is visible | `Verify`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! | ✗ `have`: You have been successfully subscribed! | ✗ `have`: You have been successfully subscribed! | ✗ `subscribed`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! |

---

## App1-TestCase2.feature
**Test Case 2: Verify Scroll Up using 'Arrow' button and Scroll Down functionality**  
URLs: http://automationexercise.com

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Scroll down page to bottom | `Scroll`: page | ✓ `Scroll`: page to bottom | ✓ `Scroll`: page to bottom | ✗ `bottom`: — | ✗ `bottom`: — | ✗ `page`: bottom | ✓ `Scroll`: page to bottom |
| 5 | Verify 'SUBSCRIPTION' is visible | `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✗ `is`: SUBSCRIPTION | ✗ `is`: SUBSCRIPTION | ✗ `is`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION |
| 6 | Click on arrow at bottom right side to move upward | `Click`: arrow | ✓ `Click`: arrow at bottom right side to move upward | ✓ `Click`: arrow at bottom right side to move upward | ✗ `move`: — | ✗ `move upward`: — | ✓ `Click`: arrow, bottom right side | ✓ `Click`: arrow at bottom right side to move upward |
| 7 | Verify that page is scrolled up and 'Full-Fledged practice website for Automation Engineers' text is visible on screen | `Verify`: Full-Fledged practice website for Automation Engineers | ✓ `Verify`: Full-Fledged practice website for Automation Engineers | ✗ `Verify`: page | ✓ `Verify`: Full-Fledged practice website for Automation Engineers | ✓ `Verify`: Full-Fledged practice website for Automation Engineers | ✗ `scrolled`: Full-Fledged practice website for Automation Engineers | ✓ `Verify`: Full-Fledged practice website for Automation Engineers |

---

## App1-TestCase3.feature
**Test Case 3: Login User with incorrect email and password**  
URLs: http://automationexercise.com, https://automationexercise.com/login

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'Signup / Login' button | `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login |
| 5 | Verify 'Login to your account' is visible | `Verify`: Login to your account | ✓ `Verify`: Login to your account | ✓ `Verify`: Login to your account | ✗ `is`: Login to your account | ✗ `is`: Login to your account | ✗ `is`: Login to your account | ✓ `Verify`: Login to your account |
| 6 | Enter incorrect email address and password | `Enter`: email address, password | ✓ `Enter`: incorrect email address, password | ✓ `Enter`: incorrect email address, password | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: incorrect email address and password, password | ✓ `Enter`: password, incorrect email address |
| 7 | Click 'login' button | `Click`: login | ✓ `Click`: login | ✓ `Click`: login | ✗ `—`: — | ✗ `—`: — | ✗ `button`: login | ✓ `Click`: login |
| 8 | Verify error 'Your email or password is incorrect!' is visible | `Verify`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! |
| 9 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 10 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 11 | Click on 'Signup / Login' button | `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login |
| 12 | Enter incorrect email address and password | `Enter`: email address, password | ✓ `Enter`: incorrect email address, password | ✓ `Enter`: incorrect email address, password | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: incorrect email address and password, password | ✓ `Enter`: password, incorrect email address |
| 13 | Click 'login' button | `Click`: login | ✓ `Click`: login | ✓ `Click`: login | ✗ `—`: — | ✗ `—`: — | ✗ `button`: login | ✓ `Click`: login |
| 14 | Verify error 'Your email or password is incorrect!' is visible | `Verify`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✗ `is`: Your email or password is incorrect! | ✓ `Verify`: Your email or password is incorrect! |

---

## App1-TestCase4.feature
**Test Case 4: Verify Subscription in Cart page**  
URLs: http://automationexercise.com, https://automationexercise.com/view_cart

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click 'Cart' button | `Click`: Cart | ✓ `Click`: Cart | ✓ `Click`: Cart | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Cart | ✓ `Click`: Cart |
| 5 | Scroll down to footer | `Scroll`: footer | ✓ `Scroll`: footer | ✓ `Scroll`: footer | ✗ `footer`: — | ✗ `footer`: — | ✓ `Scroll`: footer | ✓ `Scroll`: footer |
| 6 | Verify text 'SUBSCRIPTION' | `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION | ✗ `—`: — | ✗ `—`: — | ✓ `Verify`: SUBSCRIPTION | ✓ `Verify`: SUBSCRIPTION |
| 7 | Enter email address in input and click arrow button | `Enter`: email address ➜ `Click`: arrow button | ✓ `Enter`: email address in input ➜ `click`: arrow button | ✓ `Enter`: email address ➜ `click`: arrow button | ✗ `—`: — ➜ `—`: — | ✗ `—`: — ➜ `—`: — | ✓ `Enter`: email address ➜ `click`: arrow button | ✓ `Enter`: email address ➜ `click`: arrow button |
| 8 | Verify success message 'You have been successfully subscribed!' is visible | `Verify`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! | ✗ `have`: You have been successfully subscribed! | ✗ `have`: You have been successfully subscribed! | ✗ `subscribed`: You have been successfully subscribed! | ✓ `Verify`: You have been successfully subscribed! |

---

## App1-TestCase5.feature
**Test Case 5: Register User**  
URLs: http://automationexercise.com, https://automationexercise.com/login, https://automationexercise.com/signup

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'Signup / Login' button | `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Signup / Login | ✓ `Click`: Signup / Login |
| 5 | Verify 'New User Signup!' is visible | `Verify`: New User Signup! | ✓ `Verify`: New User Signup! | ✓ `Verify`: New User Signup! | ✗ `is`: New User Signup! | ✗ `is`: New User Signup! | ✓ `Verify`: New User Signup! | ✓ `Verify`: New User Signup! |
| 6 | Enter name and email address | `Enter`: name, email address | ✓ `Enter`: name, email address | ✓ `Enter`: name, email address | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: name and email address, email address | ✓ `Enter`: email address, name |
| 7 | Click 'Signup' button | `Click`: Signup | ✓ `Click`: Signup | ✓ `Click`: Signup | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Signup | ✓ `Click`: Signup |
| 8 | Verify that 'ENTER ACCOUNT INFORMATION' is visible | `Verify`: ENTER ACCOUNT INFORMATION | ✓ `Verify`: ENTER ACCOUNT INFORMATION | ✓ `Verify`: ENTER ACCOUNT INFORMATION | ✓ `Verify`: ENTER ACCOUNT INFORMATION | ✗ `Verify that`: ENTER ACCOUNT INFORMATION | ✗ `is`: ENTER ACCOUNT INFORMATION | ✓ `Verify`: ENTER ACCOUNT INFORMATION |
| 9 | Fill details: Title, Name, Email, Password, Date of birth | `Fill`: Title, Name, Email, Password, Date of birth | ✓ `Fill`: details: Title, Name, Email, Password, Date of birth | ✓ `Fill`: details: Title, Name, Email, Password, Date of birth | ✗ `—`: — | ✗ `—`: — | ✗ `details`: — | ✗ `Fill`: details: Title |
| 10 | Select checkbox 'Sign up for our newsletter!' | `Select`: Sign up for our newsletter! | ✓ `Select`: Sign up for our newsletter! | ✓ `Select`: checkbox Sign up for our newsletter! | ✗ `'Sign`: Sign up for our newsletter! | ✗ `'Sign up`: Sign up for our newsletter! | ✗ `Sign`: Sign up for our newsletter! | ✓ `Select`: Sign up for our newsletter! |
| 11 | Select checkbox 'Receive special offers from our partners!' | `Select`: Receive special offers from our partners! | ✓ `Select`: Receive special offers from our partners! | ✓ `Select`: checkbox Receive special offers from our partners! | ✗ `—`: — | ✗ `—`: — | ✗ `Receive`: Receive special offers from our partners! | ✓ `Select`: Receive special offers from our partners! |
| 12 | Fill details: First name, Last name, Company, Address, Address2, Country, State, City, Zipcode, Mobile Number | `Fill`: First name, Last name, Company, Address, Address2, Country, State, City, Zipcode, Mobile Number | ✓ `Fill`: details: First name, Last name, Company, Address, Address2, Country, State, City, Zipcode, Mobile Number | ✓ `Fill`: details: First name, Last name, Company, Address, Address2, Country, State, City, Zipcode, Mobile Number | ✗ `—`: — | ✗ `—`: — | ✗ `details`: — | ✗ `Fill`: details: First name |
| 13 | Click 'Create Account button' | `Click`: Create Account button | ✓ `Click`: Create Account button | ✓ `Click`: Create Account button | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Create Account button | ✓ `Click`: Create Account button |
| 14 | Verify that 'ACCOUNT CREATED!' is visible | `Verify`: ACCOUNT CREATED! | ✓ `Verify`: ACCOUNT CREATED! | ✓ `Verify`: ACCOUNT CREATED! | ✓ `Verify`: ACCOUNT CREATED! | ✓ `Verify`: ACCOUNT CREATED! | ✗ `is`: ACCOUNT CREATED! | ✓ `Verify`: ACCOUNT CREATED! |
| 15 | Click 'Continue' button | `Click`: Continue | ✓ `Click`: Continue | ✓ `Click`: Continue | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Continue | ✓ `Click`: Continue |
| 16 | Verify that 'Logged in as username' is visible | `Verify`: Logged in as username | ✓ `Verify`: Logged in as username | ✓ `Verify`: Logged in as username | ✓ `Verify`: Logged in as username | ✓ `Verify`: Logged in as username | ✗ `is`: Logged in as username | ✓ `Verify`: Logged in as username |
| 17 | Click 'Delete Account' button | `Click`: Delete Account | ✓ `Click`: Delete Account | ✓ `Click`: Delete Account | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Delete Account | ✓ `Click`: Delete Account |
| 18 | Verify that 'ACCOUNT DELETED!' is visible and click 'Continue' button | `Verify`: ACCOUNT DELETED! ➜ `Click`: Continue | ✓ `Verify`: ACCOUNT DELETED! ➜ `click`: Continue | ✓ `Verify`: ACCOUNT DELETED! ➜ `click`: Continue | ✗ `Verify`: ACCOUNT DELETED! ➜ `—`: — | ✗ `Verify`: ACCOUNT DELETED! ➜ `—`: — | ✓ `Verify`: ACCOUNT DELETED! ➜ `click`: Continue | ✓ `Verify`: ACCOUNT DELETED! ➜ `click`: Continue |

---

## App1-TestCase6.feature
**Test Case 6: Contact Us Form**  
URLs: http://automationexercise.com, https://automationexercise.com/contact_us, http://automationexercise.com

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://automationexercise.com' | `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✗ `url`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com | ✓ `Navigate`: http://automationexercise.com |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'Contact Us' button | `Click`: Contact Us | ✓ `Click`: Contact Us | ✓ `Click`: Contact Us | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Contact Us | ✓ `Click`: Contact Us |
| 5 | Verify 'GET IN TOUCH' is visible | `Verify`: GET IN TOUCH | ✓ `Verify`: GET IN TOUCH | ✓ `Verify`: GET IN TOUCH | ✗ `is`: GET IN TOUCH | ✗ `is`: GET IN TOUCH | ✗ `is`: GET IN TOUCH | ✓ `Verify`: GET IN TOUCH |
| 6 | Enter name, email, subject and message | `Enter`: name, email, subject, message | ✓ `Enter`: name, email, subject, message | ✓ `Enter`: name, email, subject, message | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: name, email, subject and message, email, subject and message, subject and message, message | ✓ `Enter`: message, name, email, subject |
| 7 | Upload file | `Upload`: file | ✓ `Upload`: file | ✓ `Upload`: file | ✗ `—`: — | ✗ `—`: — | ✗ `file`: — | ✓ `Upload`: file |
| 8 | Click 'Submit' button | `Click`: Submit | ✓ `Click`: Submit | ✓ `Click`: Submit | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Submit | ✓ `Click`: Submit |
| 9 | Click OK button | `Click`: OK | ✓ `Click`: OK button | ✓ `Click`: OK button | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: OK button | ✓ `Click`: OK button |
| 10 | Verify success message 'Success! Your details have been submitted successfully.' is visible | `Verify`: Success! Your details have been submitted successfully. | ✓ `Verify`: Success! Your details have been submitted successfully. | ✓ `Verify`: Success! Your details have been submitted successfully. | ✗ `have`: Success! Your details have been submitted successfully. | ✗ `have`: Success! Your details have been submitted successfully. | ✓ `Verify`: Success! Your details have been submitted successfully. | ✓ `Verify`: Success! Your details have been submitted successfully. |
| 11 | Click 'Home' button and verify that landed to home page successfully | `Click`: Home ➜ `Verify`: home page | ✓ `Click`: Home ➜ `verify`: landed to home page successfully | ✓ `Click`: Home ➜ `verify`: landed to home page successfully | ✗ `—`: — ➜ `landed`: home page | ✗ `—`: — ➜ `landed to`: home page | ✗ `Click`: Home ➜ `verify`: — | ✓ `Click`: Home ➜ `verify`: landed to home page successfully |

---

## App2-TestCase1.feature
**Test Case 1: Successfully Search for a Movie**  
URLs: http://localhost:5173/

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on the search input labeled 'Digite o nome do filme' | `Click`: Digite o nome do filme | ✓ `Click`: Digite o nome do filme | ✓ `Click`: the search input labeled Digite o nome do filme | ✗ `labeled`: Digite o nome do filme | ✗ `labeled`: Digite o nome do filme | ✓ `Click`: Digite o nome do filme | ✓ `Click`: Digite o nome do filme |
| 5 | Enter movie name 'Interestellar' | `Enter`: Interestellar | ✓ `Enter`: Interestellar | ✓ `Enter`: movie name Interestellar | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: Interestellar | ✓ `Enter`: Interestellar |
| 6 | Verify that the movie card titled 'Interstellar' is visible | `Verify`: Interstellar | ✓ `Verify`: Interstellar | ✓ `Verify`: the movie card titled Interstellar | ✓ `Verify`: Interstellar | ✗ `Verify that`: Interstellar | ✓ `Verify`: Interstellar | ✓ `Verify`: Interstellar |

---

## App2-TestCase2.feature
**Test Case 6: Successfully Filter Movies by State**  
URLs: http://localhost:5173/

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on the select dropdown labeled 'Estado' | `Click`: Estado | ✓ `Click`: Estado | ✓ `Click`: the select dropdown labeled Estado | ✗ `labeled`: Estado | ✗ `labeled`: Estado | ✓ `Click`: Estado | ✓ `Click`: Estado |
| 5 | Select the option 'AM' from the list | `Select`: AM | ✓ `Select`: AM | ✓ `Select`: the option AM from the list | ✓ `Select`: AM | ✓ `Select`: AM | ✓ `Select`: AM | ✓ `Select`: AM |
| 6 | Verify that the movie card titled 'Joker' is visible | `Verify`: Joker | ✓ `Verify`: Joker | ✓ `Verify`: the movie card titled Joker | ✓ `Verify`: Joker | ✗ `Verify that`: Joker | ✓ `Verify`: Joker | ✓ `Verify`: Joker |

---

## App2-TestCase3.feature
**Test Case 3: Unsuccessfully Login with Incorrect Credentials**  
URLs: http://localhost:5173/, http://localhost:5173/LogIn

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'LogIn' button | `Click`: LogIn | ✓ `Click`: LogIn | ✓ `Click`: LogIn | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: LogIn | ✓ `Click`: LogIn |
| 5 | Verify 'Log In' is visible | `Verify`: Log In | ✓ `Verify`: Log In | ✓ `Verify`: Log In | ✗ `is`: Log In | ✗ `is`: Log In | ✗ `is`: Log In | ✓ `Verify`: Log In |
| 6 | Enter incorrect email and password | `Enter`: email, password | ✓ `Enter`: incorrect email, password | ✓ `Enter`: incorrect email, password | ✗ `—`: — | ✗ `—`: — | ✓ `Enter`: incorrect email and password, password | ✓ `Enter`: password, incorrect email |
| 7 | Click 'Log In' button | `Click`: Log In | ✓ `Click`: Log In | ✓ `Click`: Log In | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Log In | ✓ `Click`: Log In |
| 8 | Verify error message 'User not found!' is visible | `Verify`: User not found! | ✓ `Verify`: User not found! | ✓ `Verify`: User not found! | ✗ `found`: User not found! | ✗ `found`: User not found! | ✓ `Verify`: User not found! | ✓ `Verify`: User not found! |

---

## App2-TestCase4.feature
**Test Case 4: Successfully Navigate to Movie Details Page**  
URLs: http://localhost:5173/, http://localhost:5173/MovieSession/

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on the movie card titled 'Barbie' | `Click`: Barbie | ✓ `Click`: Barbie | ✓ `Click`: the movie card titled Barbie | ✗ `titled`: Barbie | ✗ `titled`: Barbie | ✓ `Click`: Barbie | ✓ `Click`: Barbie |
| 5 | Verify that the movie details page for 'Barbie' is visible | `Verify`: Barbie | ✓ `Verify`: Barbie | ✓ `Verify`: the movie details page for Barbie | ✓ `Verify`: Barbie | ✗ `Verify that`: Barbie | ✓ `Verify`: Barbie | ✓ `Verify`: Barbie |

---

## App2-TestCase5.feature
**Test Case 5: Successfully Register a New User**  
URLs: http://localhost:5173/, http://localhost:5173/LogIn, http://localhost:5173/SignUp

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'LogIn' button | `Click`: LogIn | ✓ `Click`: LogIn | ✓ `Click`: LogIn | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: LogIn | ✓ `Click`: LogIn |
| 5 | Verify 'Log In' is visible | `Verify`: Log In | ✓ `Verify`: Log In | ✓ `Verify`: Log In | ✗ `is`: Log In | ✗ `is`: Log In | ✗ `is`: Log In | ✓ `Verify`: Log In |
| 6 | Click on 'SignUp' button | `Click`: SignUp | ✓ `Click`: SignUp | ✓ `Click`: SignUp | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: SignUp | ✓ `Click`: SignUp |
| 7 | Verify 'Sign Up' is visible | `Verify`: Sign Up | ✓ `Verify`: Sign Up | ✓ `Verify`: Sign Up | ✗ `is`: Sign Up | ✗ `is`: Sign Up | ✗ `is`: Sign Up | ✓ `Verify`: Sign Up |
| 8 | Enter first name, last name, email, confirm email, password, and confirm password | `Enter`: first name, last name, email, confirm email, password, confirm password | ✓ `Enter`: first name, last name, email, confirm email, password, and confirm password | ✓ `Enter`: first name, last name, email, confirm email, password, and confirm password | ✗ `—`: — | ✗ `—`: — | ✗ `Enter`: first name, last name, email, | ✓ `Enter`: first name, last name, email, confirm email, password, and confirm password |
| 9 | Click 'Sign Up' button | `Click`: Sign Up | ✓ `Click`: Sign Up | ✓ `Click`: Sign Up | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Sign Up | ✓ `Click`: Sign Up |
| 10 | Verify success message 'Registration completed successfully!' is visible | `Verify`: Registration completed successfully! | ✓ `Verify`: Registration completed successfully! | ✓ `Verify`: Registration completed successfully! | ✗ `completed`: Registration completed successfully! | ✗ `completed successfully`: Registration completed successfully! | ✓ `Verify`: Registration completed successfully! | ✓ `Verify`: Registration completed successfully! |

---

## App2-TestCase6.feature
**Test Case 6: Successfully Register a New Movie**  
URLs: http://localhost:5173/, http://localhost:5173/CreateMovie

| # | Step | Ground Truth | M1 Regex | M2 Keyword | M3 NLTK POS | M4 NLTK Chunk | M5 spaCy | M6 Ensemble |
|---|------|-------------|---------|---------|---------|---------|---------|---------|
| 1 | Launch browser | `Launch`: browser | ✓ `Launch`: browser | ✓ `Launch`: browser | ✗ `—`: — | ✗ `—`: — | ✗ `browser`: — | ✓ `Launch`: browser |
| 2 | Navigate to url 'http://localhost:5173/' | `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✗ `url`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ | ✓ `Navigate`: http://localhost:5173/ |
| 3 | Verify that home page is visible successfully | `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: home page | ✓ `Verify`: that home page | ✓ `Verify`: that home page | ✗ `is`: — | ✓ `Verify`: home page |
| 4 | Click on 'CreateMovie' button | `Click`: CreateMovie | ✓ `Click`: CreateMovie | ✓ `Click`: CreateMovie | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: CreateMovie | ✓ `Click`: CreateMovie |
| 5 | Fill in all required fields: url cartaz, nome, descrição, faixa etária, diretor(a), escritor(a), ator(a), gênero, and data de lançamento | `Fill`: url cartaz, nome, descrição, faixa etária, diretor(a), escritor(a), ator(a), gênero, data de lançamento | ✓ `Fill`: all required fields: url cartaz, nome, descrição, faixa etária, diretor(a), escritor(a), ator(a), gênero, and data de lançamento | ✓ `Fill`: all required fields: url cartaz, nome, descrição, faixa etária, diretor(a), escritor(a), ator(a), gênero, and data de lançamento | ✗ `—`: — | ✗ `—`: — | ✗ `Fill`: all required fields | ✓ `Fill`: all required fields: url cartaz, nome, descrição, faixa etária, diretor(a), escritor(a), ator(a), gênero, and data de lançamento |
| 6 | Click 'Criar' button | `Click`: Criar | ✓ `Click`: Criar | ✓ `Click`: Criar | ✗ `—`: — | ✗ `—`: — | ✓ `Click`: Criar | ✓ `Click`: Criar |
| 7 | Verify success message 'Film Created Successfully!' is visible | `Verify`: Film Created Successfully! | ✓ `Verify`: Film Created Successfully! | ✓ `Verify`: Film Created Successfully! | ✗ `is`: Film Created Successfully! | ✗ `is`: Film Created Successfully! | ✓ `Verify`: Film Created Successfully! | ✓ `Verify`: Film Created Successfully! |

---
