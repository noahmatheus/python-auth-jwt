import re
import requests
from docling import DocumentConverter
# from firecrawl import FirecrawlClient  # se quiser usar no futuro
# from doclingstate import extract_blocks  # se quiser usar blocos visuais

def scrape_website(url: str, engine: str = "docling") -> str:
    """
    Faz scraping de uma URL e retorna o conteúdo em Markdown limpo.
    
    Args:
        url (str): A URL a ser raspada.
        engine (str): O mecanismo de scraping ("docling", "firecrawl", "doclingstate").
        
    Returns:
        str: Conteúdo extraído em Markdown limpo.
    """
    print(f"🔍 Iniciando scraping com engine '{engine}': {url}")
    
    try:
        if engine == "docling":
            converter = DocumentConverter()
            result = converter.convert(url)
            markdown = result.document.export_to_markdown()
        
        elif engine == "firecrawl":
            raise NotImplementedError("Firecrawl ainda não está configurado neste projeto.")
            # Exemplo:
            # client = FirecrawlClient(api_key="SUA_API_KEY")
            # result = client.crawl(url)
            # markdown = result['markdown']
        
        elif engine == "doclingstate":
            raise NotImplementedError("DoclingState ainda não foi integrado.")
            # Exemplo:
            # markdown = extract_blocks(url)  # Assumindo que você criou um extrator personalizado
        
        else:
            raise ValueError(f"Engine '{engine}' não reconhecido. Use 'docling', 'firecrawl' ou 'doclingstate'.")

        # Limpeza básica: remove barras invertidas em links
        markdown_limpo = re.sub(r'https://[^\s)]+', lambda m: m.group(0).replace('\\', ''), markdown)

        print("✅ Scraping finalizado com sucesso.")
        return markdown_limpo

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de rede ao acessar a URL: {e}")
    except Exception as e:
        print(f"❌ Erro durante o scraping: {e}")
    
    return ""  # Retorna string vazia se houver erro
