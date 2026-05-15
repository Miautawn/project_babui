from playwright.async_api import Page


async def enable_visual_mouse(page: Page):
    # This single string works for BOTH immediate injection and future reloads
    unified_js = """
    (() => {
        const createTarget = () => {
            if (document.getElementById('sniper-mouse')) return;

            const dot = document.createElement('div');
            dot.id = 'sniper-mouse';
            Object.assign(dot.style, {
                position: 'fixed',
                width: '12px',
                height: '12px',
                backgroundColor: 'red',
                border: '2px solid white',
                borderRadius: '50%',
                zIndex: '2147483647',
                pointerEvents: 'none',
                top: '0px',
                left: '0px',
                transform: 'translate(-50%, -50%)',
                transition: 'top 0.03s linear, left 0.03s linear'
            });

            document.body.appendChild(dot);

            window.addEventListener('mousemove', e => {
                dot.style.left = `${e.clientX}px`;
                dot.style.top = `${e.clientY}px`;
            });

            // Visual feedback for clicks
            window.addEventListener('mousedown', () => { dot.style.backgroundColor = 'lime'; });
            window.addEventListener('mouseup', () => { dot.style.backgroundColor = 'red'; });
        };

        // Execution Logic:
        // If the body exists (evaluate), run now.
        // If not (init_script), wait for the body to appear.
        if (document.body) {
            createTarget();
        } else {
            window.addEventListener('DOMContentLoaded', createTarget);
        }
    })()
    """

    # Register it for the future
    await page.add_init_script(unified_js)
    # Inject it for right now
    await page.evaluate(unified_js)
