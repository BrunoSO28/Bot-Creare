from playwright.async_api import async_playwright
import asyncio
import os

async def zap():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./whatsapp_session",  # salva a sessão/QR Code
            headless=False
        )
        
        page = await browser.new_page()
        await page.goto("https://web.whatsapp.com/")
        await page.wait_for_timeout(500)
        await page.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("Estágio")
        await page.wait_for_timeout(500)
        await page.get_by_text("Estágio").click()
        await page.wait_for_timeout(500)
        diretorio = os.getcwd()
        diretorioFinal = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera.mp4")
        await page.get_by_role("button", name="Anexar").click()
        await page.click('button[aria-label="Fotos e vídeos"]')
        await page.wait_for_timeout(500)
        await page.locator('input[accept="image/*,video/mp4,video/3gpp,video/quicktime,video/webm,video/x-matroska"]').set_input_files(diretorioFinal)
        await page.get_by_test_id("media-caption-input-container").get_by_role("paragraph").fill("Teste 1231!!!!")
        await page.wait_for_timeout(500)
        await page.get_by_role("button", name="Enviar 1 item selecionado").click()
        await page.wait_for_timeout(3000)
        await browser.close()

asyncio.run(zap())