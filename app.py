from flask import Flask, request, render_template_string, session, redirect, url_for
from bs4 import BeautifulSoup
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

uploader_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IntelliNet - Voice-Controlled Web Navigation System</title>
    <style>
      /* General Reset */
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: "Arial", sans-serif;
        background-color: #000;
        color: #fff;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        padding: 20px;
      }

      header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #fff;
      }

      header h1 {
        font-size: 3rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
      }

      header h2 {
        font-size: 1.5rem;
        margin-bottom: 20px;
        font-weight: 300;
      }

      .instructions {
        max-width: 800px;
        margin: 20px auto;
        padding: 20px;
        background: linear-gradient(145deg, #111, #000);
        border: 1px solid #fff;
        border-radius: 10px;
        text-align: left;
        line-height: 1.8;
      }

      .instructions h3 {
        font-size: 1.5rem;
        margin-bottom: 10px;
        text-align: center;
      }

      .instructions p {
        font-size: 1rem;
        margin-bottom: 10px;
      }

      .upload-form {
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 600px;
        margin: 20px auto;
        padding: 20px;
        border: 1px solid #fff;
        border-radius: 10px;
        background: linear-gradient(145deg, #111, #000);
      }

      .upload-form label {
        font-size: 1.2rem;
        margin-bottom: 10px;
      }

      .upload-form input[type="file"] {
        font-size: 1rem;
        padding: 10px;
        border: 1px solid #fff;
        background-color: #000;
        color: #fff;
        border-radius: 5px;
        width: 100%;
        max-width: 400px;
        cursor: pointer;
        text-align: center;
        margin-bottom: 20px;
      }

      .upload-form input[type="file"]::file-selector-button {
        background-color: #fff;
        color: #000;
        border: 1px solid #fff;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
      }

      .upload-form input[type="file"]::file-selector-button:hover {
        background-color: #ccc;
      }

      .upload-form button {
        background-color: #fff;
        color: #000;
        border: 1px solid #fff;
        padding: 10px 20px;
        font-size: 1rem;
        cursor: pointer;
        border-radius: 5px;
        transition: all 0.3s ease-in-out;
      }

      .upload-form button:hover {
        background-color: #ccc;
        color: #000;
      }

      footer {
        text-align: center;
        padding: 20px 0;
        border-top: 1px solid #fff;
        margin-top: auto;
      }

      footer p {
        font-size: 1rem;
      }

      /* Responsive Design */
      @media (max-width: 768px) {
        header h1 {
          font-size: 2rem;
        }

        header h2 {
          font-size: 1.2rem;
        }

        .instructions h3 {
          font-size: 1.2rem;
        }

        .upload-form input[type="file"],
        .upload-form button {
          font-size: 0.9rem;
        }
      }
    </style>
  </head>
  <body>
    <header>
      <h1>IntelliNet</h1>
      <h2>Voice-Controlled Web Navigation Made Simple</h2>
    </header>

    <div class="instructions">
      <h3>Instructions</h3>
      <p>✔ You can upload one or more HTML files.</p>
      <p>✔ The files must have the extension <code>.htm</code> or <code>.html</code>.</p>
      <p>
        ✔ After uploading, download the generated JavaScript file and add it to
        your website.
      </p>
      <p>✔ You're all set to enjoy voice-controlled web navigation!</p>
    </div>

    <form
      class="upload-form"
      action="/process"
      method="post"
      enctype="multipart/form-data"
    >
      <label for="htmlfiles">Choose HTML files:</label>
      <input
        type="file"
        id="htmlfiles"
        name="htmlfiles"
        accept=".html"
        multiple
        required
      />
      <button type="submit">Upload Files</button>
    </form>

    <footer>
      <p>
        © 2024 IntelliNet. All rights reserved. | Simplifying web navigation
        with voice assistance.
      </p>
    </footer>
  </body>
</html>
"""

@app.route('/')
def upload_page():
    return render_template_string(uploader_html)

@app.route('/process', methods=['POST'])
def process_file():
    uploaded_files = request.files.getlist('htmlfiles')
    if not uploaded_files:
        return "No files uploaded. Please select valid HTML files.", 400

    elements_data = {'buttons': [], 'anchors': [], 'nav_anchors': []}

    try:
        for uploaded_file in uploaded_files:
            if not uploaded_file.filename.endswith('.html'):
                return "Invalid file type. Only HTML files are allowed.", 400

            html_content = uploaded_file.read()
            soup = BeautifulSoup(html_content, 'html.parser')

            for btn in soup.find_all('button'):
                btn_id = btn.get('id', f"btn-{uuid.uuid4().hex[:8]}")
                btn['id'] = btn_id
                btn_text = btn.text.strip()
                elements_data['buttons'].append({'id': btn_id, 'text': btn_text, 'tag': 'button'})

            for anchor in soup.find_all('a', href=True):
                parent_nav = anchor.find_parent('nav')
                if not parent_nav:
                    anchor_id = anchor.get('id', f"a-{uuid.uuid4().hex[:8]}")
                    anchor['id'] = anchor_id
                    elements_data['anchors'].append({
                        'id': anchor_id,
                        'text': anchor.text.strip(),
                        'href': anchor['href'],
                        'tag': 'a'
                    })

            for nav in soup.find_all('nav'):
                for nav_anchor in nav.find_all('a', href=True):
                    nav_anchor_id = nav_anchor.get('id', f"nav-a-{uuid.uuid4().hex[:8]}")
                    nav_anchor['id'] = nav_anchor_id
                    elements_data['nav_anchors'].append({
                        'id': nav_anchor_id,
                        'text': nav_anchor.text.strip(),
                        'href': nav_anchor['href'],
                        'tag': 'nav-a'
                    })

        session['elements_data'] = elements_data
        return redirect(url_for('select_components'))

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the files.", 500
   

@app.route('/select-components')
def select_components():
    elements_data = session.get('elements_data', {'buttons': [], 'anchors': [], 'nav_anchors': []})

    return render_template_string("""
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Components</title>
    <style>
        /* General Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
            font-family: "Arial", sans-serif;
            background-color: #000;
            color: #fff;
        }

        body {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 20px 0;
            width: 100%;
            border-bottom: 1px solid #fff;
        }

        header h1 {
            font-size: 2.5rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        form {
            width: 100%;
            margin: 20px auto;
            padding: 20px;
            background: linear-gradient(145deg, #111, #000);
            border: 1px solid #fff;
            border-radius: 10px;
        }

        h2 {
            font-size: 1.5rem;
            margin-bottom: 10px;
            text-align: center;
            text-transform: uppercase;
        }

        .component {
    margin: 10px 0;
    padding: 15px;
    border: 1px solid #fff;
    border-radius: 10px;
    background: #111;
    display: flex;
    align-items: center; /* Align items vertically in the center */
    width: 100%;
    gap: 10px; /* Add spacing between elements */
}

.component input[type="checkbox"] {
    margin: 0; /* Remove default margin for consistency */
    cursor: pointer;
}

.component label {
    font-size: 1rem;
    flex-grow: 1; /* Allow label to grow and take up space */
}

.component input[type="text"] {
    width: 50%; /* Adjust width as needed */
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #fff;
    background-color: #000;
    color: #fff;
    border-radius: 5px;
}

        .component input[type="text"]::placeholder {
            color: #ccc;
        }

        button {
            width: 100%;
            padding: 15px;
            font-size: 1rem;
            background-color: #fff;
            color: #000;
            border: none;
            border-radius: 10px;
            text-transform: uppercase;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #ccc;
        }

        footer {
            text-align: center;
            width: 100%;
            padding: 20px 0;
            border-top: 1px solid #fff;
        }

        footer p {
            font-size: 0.9rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            header h1 {
                font-size: 2rem;
            }

            h2 {
                font-size: 1.2rem;
            }

            .component input[type="text"] {
                font-size: 0.9rem;
            }

            button {
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Select Components</h1>
    </header>
    <form action="/generate" method="post">
        <h2>Buttons</h2>
        {% for button in buttons %}
        <div class="component">
            <input type="checkbox" name="components" value="{{ button.id }}">
            <label for="{{ button.id }}">ID: {{ button.id }}, Text: {{ button.text }}</label>
            <input type="text" name="names[{{ button.id }}]" placeholder="Enter name/command">
        </div>
        {% endfor %}

        <h2>Standalone Anchors</h2>
        {% for anchor in anchors %}
        <div class="component">
            <input type="checkbox" name="components" value="{{ anchor.id }}">
            <label for="{{ anchor.id }}">ID: {{ anchor.id }}, Text: {{ anchor.text }}, Href: {{ anchor.href }}</label>
            <input type="text" name="names[{{ anchor.id }}]" placeholder="Enter name/command">
        </div>
        {% endfor %}

        <h2>Navbar Anchors</h2>
        {% for nav_anchor in nav_anchors %}
        <div class="component">
            <input type="checkbox" name="components" value="{{ nav_anchor.id }}">
            <label for="{{ nav_anchor.id }}">ID: {{ nav_anchor.id }}, Text: {{ nav_anchor.text }}, Href: {{ nav_anchor.href }}</label>
            <input type="text" name="names[{{ nav_anchor.id }}]" placeholder="Enter name/command">
        </div>
        {% endfor %}

        <button type="submit">Generate</button>
    </form>
    <footer>
        <p>© 2024 Professional Design. All rights reserved.</p>
    </footer>
</body>
</html>
    """, buttons=elements_data['buttons'], anchors=elements_data['anchors'], nav_anchors=elements_data['nav_anchors'])


    


@app.route('/generate', methods=['POST'])
def generate_results():
    selected_components = request.form.getlist('components')
    component_names = request.form.to_dict(flat=False)
    if not selected_components:
        return "No components selected.", 400

    elements_data = session.get('elements_data', {})
    json_data = []

    # Prepare selected component data
    for component_id in selected_components:
        name = component_names.get(f"names[{component_id}]", [f"default_name_{component_id}"])[0]
        for category in ['buttons', 'anchors', 'nav_anchors']:
            component = next((item for item in elements_data[category] if item['id'] == component_id), None)
            if component:
                component_data = {**component, 'name': name}
                json_data.append(component_data)
                break

    # Save to JSON
    try:
        json_file_path = "selected_components.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while saving the data.", 500

    js_code = generate_js_code(json_data)

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results</title>
    <style>
        /* General Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Arial", sans-serif;
            background-color: #000;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            min-height: 100vh;
        }

        h1 {
            font-size: 2.5rem;
            text-transform: uppercase;
            margin: 20px 0;
            text-align: center;
            color: #fff;
        }

        ul {
            list-style: none;
            width: 100%;
            max-width: 800px;
            background: linear-gradient(145deg, #111, #000);
            border: 1px solid #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            padding: 20px;
            margin-bottom: 20px;
            overflow: hidden;
        }

        ul li {
            font-size: 1.2rem;
            margin-bottom: 10px;
            line-height: 1.8;
        }

        iframe {
            width: 100%;
            max-width: 800px;
            height: 300px;
            border: 1px solid #fff;
            border-radius: 10px;
            background: #111;
            overflow-y: auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }

        .iframe-container pre {
            font-family: "Courier New", monospace;
            color: #fff;
            padding: 20px;
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #000;
            line-height: 1.6;
        }

        .button-container {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }

        button {
            background-color: #fff;
            color: #000;
            border: 1px solid #fff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            text-transform: uppercase;
            transition: all 0.3s ease-in-out;
        }

        button:hover {
            background-color: #ccc;
            color: #000;
        }

        p {
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            iframe {
                height: 250px;
            }

            button {
                font-size: 0.9rem;
                padding: 10px 15px;
            }

            ul li {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <h1>Selected Components</h1>
    <ul>
        {% for result in results %}
            <li>ID: {{ result.id }}, Name/Command: {{ result.name }}</li>
        {% endfor %}
    </ul>

    <h1>Generated JavaScript Code</h1>
    <p>Preview the generated JavaScript code below:</p>

    <iframe id="js-iframe" srcdoc="
    <html>
    <body style='margin:0; font-family:Courier New, monospace; background-color:#000; color:#fff;'>
    <pre style='font-size: 16px; line-height: 1.8;'>{{ js_code | e }}</pre>
    </body>
    </html>"></iframe>

    <div class="button-container">
        <button id="copy-js">Copy JavaScript Code</button>
        <button id="download-js">Download JavaScript File</button>
    </div>

    <script>
        // Copy JavaScript code to clipboard
        document.getElementById('copy-js').addEventListener('click', function () {
            const iframe = document.getElementById('js-iframe');
            const code = iframe.contentDocument.querySelector('pre').textContent;

            navigator.clipboard.writeText(code).then(function () {
                alert('JavaScript code copied to clipboard!');
            }).catch(function (err) {
                console.error('Failed to copy code:', err);
            });
        });

        // Download JavaScript code as a file
        document.getElementById('download-js').addEventListener('click', function () {
            const iframe = document.getElementById('js-iframe');
            const code = iframe.contentDocument.querySelector('pre').textContent;

            const blob = new Blob([code], { type: 'application/javascript' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'generated_code.js';
            link.click();
        });
    </script>
</body>
</html>
""", results=json_data, js_code=js_code)


def generate_js_code(selected_components):
    """
    Generate JavaScript code based on the selected components
    """
    js_code = """// Initialize Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.continuous = true;
recognition.lang = 'en-US';

let isStoppedManually = false; // Flag to track manual stop

// Dynamically create the output div
let output = document.getElementById('output');
if (!output) {
    output = document.createElement('div'); // Create the output div if it doesn't exist
    output.id = 'output';
    output.textContent = 'Say "add task" to create a to-do.';
    document.body.appendChild(output); // Append it to the body
}

// Start speech recognition automatically when the page loads
window.addEventListener('DOMContentLoaded', () => {
    recognition.start();
    output.textContent = 'Voice recognition started automatically!';
});

recognition.addEventListener('end', () => {
    if (!isStoppedManually) {
        recognition.start();
        output.textContent = 'Voice recognition restarted automatically!';
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key.toLowerCase() === 'v') { 
        isStoppedManually = false; 
        recognition.start();
        output.textContent = 'Voice recognition started!';
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key.toLowerCase() === 'q') { 
        isStoppedManually = true; 
        recognition.stop();
        output.textContent = 'Voice recognition stopped!';
    }
});

recognition.addEventListener('result', (event) => {
    const transcript = event.results[event.resultIndex][0].transcript.toLowerCase();
    output.textContent = transcript;

    // Example Commands
    if (transcript.includes('scroll up')) {
        window.scrollBy(0, -500);
        output.textContent += ' - Scrolled up!';
    }

    if (transcript.includes('scroll down')) {
        window.scrollBy(0, 500);
        output.textContent += ' - Scrolled down!';
    }

    if (transcript.includes('go back')) {
        window.history.back();
        output.textContent += ' - Navigated back!';
    }
"""

    # Generate commands based on selected components
    for component in selected_components:
        component_id = component['id']
        name = component['name']
        tag = component.get('tag')
        href=component.get('href')

        # Generate commands for buttons
        if tag == 'button':
            js_code += f"""
    if (transcript.includes('{name.lower()}')) {{
    const {component_id.replace('-', '_')} = document.getElementById('{component_id}');
    if ({component_id.replace('-', '_')}) {{
        {component_id.replace('-', '_')}.click();
        output.textContent += ' - {name} button clicked!';
    }} else {{
        output.textContent += ' - {name} button not found!';
    }}
}}
"""
       

        # Generate commands for anchors
        elif tag == 'a':
            js_code += f"""
    if (transcript.includes('{name.lower()}')) {{
        const component_id = document.getElementById('{component_id}');
        if (component_id) {{
            component_id.click();
            output.textContent += ' - Navigating to {name}!';
        }} else {{
            output.textContent += ' - {name} anchor not found!';
        }}
    }}
"""

        # Generate commands for navbar anchors
        elif tag == 'nav-a':
            href = component.get('href')
            
            if href:  # Check if href is not None or empty
                href = href.replace('#', '')  # Remove the '#' from href if present
            else:
                href = ''  # Set it to an empty string if href is None
            js_code += f"""
    if (transcript.includes('go to {name.lower()}')) {{
        scrollToSection('{href}');
        output.textContent += ' - Scrolled to {name.lower()}!';
    }}
"""


    js_code += """
});
// Error handling for speech recognition
recognition.addEventListener('error', (event) => {
    console.error('Error:', event.error);
    output.textContent = `Error: ${event.error}`;
});

// Function to smoothly scroll to a specific section
function scrollToSection(sectionId) {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
}

// Ensure 'Let's Connect' button scrolls to section
document.getElementById('connect')?.addEventListener('click', () => scrollToSection("let us connect"));
"""

    return js_code

if __name__ == '__main__':  # Corrected this line
    app.run(debug=True)
