# Fix jQuery duplicate imports in index.html
content = open('www/index.html', 'r', encoding='utf-16').read()

old = """<!--Jquery  -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>

    <!-- Bootstrap -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
        crossorigin="anonymous"></script>

    <!-- Particle js -->
    <script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>
    <script src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js'></script>
    <script src="script.js"></script>

    <!-- Siri wave -->
    <script src="https://unpkg.com/siriwave/dist/siriwave.umd.min.js"></script>

    <!-- Texllate js -->
    <script src="assets/vendore/texllate/jquery.fittext.js"></script>
    <script src="assets/vendore/texllate/jquery.lettering.js"></script>
    <script src="http://jschr.github.io/textillate/jquery.textillate.js"></script>

    <script src="main.js"></script>
    <script src="controller.js"></script>
    <script src="/eel.js"></script>"""

new = """<!--Jquery  -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>

    <!-- jQuery UI -->
    <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js"></script>

    <!-- Bootstrap -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
        crossorigin="anonymous"></script>

    <!-- Texllate js -->
    <script src="assets/vendore/texllate/jquery.fittext.js"></script>
    <script src="assets/vendore/texllate/jquery.lettering.js"></script>
    <script src="http://jschr.github.io/textillate/jquery.textillate.js"></script>

    <!-- Siri wave -->
    <script src="https://unpkg.com/siriwave/dist/siriwave.umd.min.js"></script>

    <!-- App scripts -->
    <script src="script.js"></script>
    <script src="main.js"></script>
    <script src="controller.js"></script>
    <script src="/eel.js"></script>"""

if old in content:
    content = content.replace(old, new)
    open('www/index.html', 'w', encoding='utf-8').write(content)
    print('Fixed! Removed duplicate jQuery 2.1.3')
else:
    print('Old pattern not found')
