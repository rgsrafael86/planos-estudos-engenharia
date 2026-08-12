import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject CSS
css_to_inject = '''
        /* Filters */
        .filter-container {
            max-width: 1000px;
            margin: 0 auto 3rem;
            padding: 0 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            justify-content: center;
            animation: slideUp 1s ease-out 0.5s forwards;
            opacity: 0;
        }

        .filter-chip {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 8px 16px;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .filter-chip:hover {
            border-color: var(--primary-neon);
            color: var(--text-light);
        }

        .filter-chip.active {
            background: rgba(56, 189, 248, 0.2);
            border-color: var(--primary-neon);
            color: var(--primary-neon);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        }
'''
content = content.replace('/* Shelves (Disciplines) */', css_to_inject + '\n        /* Shelves (Disciplines) */')

# 2. Inject HTML container
html_to_inject = '''
    <div id="filters" class="filter-container">
        <!-- Filtros injetados via JS -->
    </div>
'''
content = content.replace('</header>', '</header>\n' + html_to_inject)

# 3. Modify JS to render filters and handle clicks
js_render_filters = '''
            // Renderizar Filtros
            const filterContainer = document.getElementById('filters');
            let filterHTML = <button class="filter-chip active" data-filter="all">Todas as Disciplinas</button>;
            Object.keys(disciplinasMap).sort().forEach(disc => {
                filterHTML += <button class="filter-chip" data-filter=""></button>;
            });
            if (filterContainer) filterContainer.innerHTML = filterHTML;
'''

content = content.replace('// Build Shelves', js_render_filters + '\n            // Build Shelves')

# 4. Modify shelf building to add data-discipline
content = content.replace('<div class="shelf">', '<div class="shelf" data-discipline="">')

# 5. Add event listener at the end of init function
js_listeners = '''
            // EventListeners para os Filtros
            document.querySelectorAll('.filter-chip').forEach(chip => {
                chip.addEventListener('click', (e) => {
                    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                    e.target.classList.add('active');
                    
                    const filter = e.target.getAttribute('data-filter');
                    
                    document.querySelectorAll('.shelf').forEach(shelf => {
                        if(filter === 'all' || shelf.getAttribute('data-discipline') === filter) {
                            shelf.style.display = 'block';
                        } else {
                            shelf.style.display = 'none';
                        }
                    });
                });
            });
        }

        window.onload = init;
'''
content = content.replace('        }\n\n        window.onload = init;', js_listeners)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.html successfully")
