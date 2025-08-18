"""
Aplicação principal de Ordem de Serviço - Versão Modular
Máximo 200 linhas - Responsabilidades divididas em módulos
"""

import os
import sys

# Se este módulo for executado diretamente (python app/main_app.py), garantir que a
# raiz do projeto esteja no sys.path para que `import app.*` funcione.
if __package__ is None:
    project_root = os.path.dirname(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY

from app.ui.formulario_tab import FormularioTab
from app.ui.database_tab import DatabaseTab


class MainApp:
    """
    Aplicação principal modularizada da Ordem de Serviço.
    Coordena as diferentes abas e funcionalidades.
    """
    
    def __init__(self, root):
        """
        Inicializa a aplicação principal.
        
        Args:
            root: Janela principal do tkinter
        """
        self.root = root
        self.root.title("Sistema de Ordem de Serviço")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximizar no Windows
        
        # Configurar estilo
        self._setup_style()
        
        # Criar interface
        self._setup_interface()
        
        # Carregar dados iniciais
        self._load_initial_data()
    
    def _setup_style(self):
        """Configura o estilo da aplicação"""
        style = tb.Style()
        
        # Configurações do tema
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
    
    def _setup_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = tb.Label(
            main_frame, 
            text="Sistema de Ordem de Serviço", 
            style='Title.TLabel',
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook principal
        self.notebook = tb.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Criar abas
        self._create_tabs()
        
        # Barra de status
        self._create_status_bar(main_frame)
    
    def _create_tabs(self):
        """Cria as abas da aplicação"""
        # Aba Formulário
        formulario_frame = tb.Frame(self.notebook)
        self.notebook.add(formulario_frame, text="📝 Formulário")
        self.formulario_tab = FormularioTab(formulario_frame)
        
        # Aba Banco de Dados
        database_frame = tb.Frame(self.notebook)
        self.notebook.add(database_frame, text="🗄️ Banco de Dados")
        self.database_tab = DatabaseTab(database_frame)
        
        # Conectar eventos entre abas
        self._connect_tab_events()
    
    def _connect_tab_events(self):
        """Conecta eventos entre as abas"""
        # Quando um formulário for enviado, atualizar a aba de dados
        # (Implementar callbacks conforme necessário)
        pass
    
    def _create_status_bar(self, parent):
        """Cria barra de status"""
        status_frame = tb.Frame(parent)
        status_frame.pack(fill="x", pady=(10, 0))
        
        # Status da conexão com banco
        self.status_label = tb.Label(
            status_frame, 
            text="🟢 Conectado ao banco de dados", 
            style='Info.TLabel'
        )
        self.status_label.pack(side="left")
        
        # Informações do sistema
        from datetime import datetime
        date_label = tb.Label(
            status_frame,
            text=f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            style='Info.TLabel'
        )
        date_label.pack(side="right")
    
    def _load_initial_data(self):
        """Carrega dados iniciais"""
        try:
            # Testar conexão com banco
            from database import db_manager
            clientes = db_manager.listar_clientes(1)
            
            if clientes is not None:
                self.status_label.config(text="🟢 Banco de dados conectado")
            else:
                self.status_label.config(text="🟡 Banco vazio - pronto para uso")
                
        except Exception as e:
            self.status_label.config(text=f"🔴 Erro no banco: {str(e)[:50]}...")
            print(f"Erro ao conectar banco: {e}")
    
    def refresh_all_data(self):
        """Atualiza dados de todas as abas"""
        try:
            self.database_tab.refresh_data()
            self.status_label.config(text="🔄 Dados atualizados")
        except Exception as e:
            self.status_label.config(text=f"❌ Erro ao atualizar: {str(e)[:30]}...")
    
    def show_notification(self, message, type_="info"):
        """
        Mostra notificação na barra de status
        
        Args:
            message (str): Mensagem a ser exibida
            type_ (str): Tipo da notificação (info, success, error)
        """
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "error": "❌",
            "warning": "⚠️"
        }
        
        icon = icons.get(type_, "ℹ️")
        self.status_label.config(text=f"{icon} {message}")
        
        # Auto-limpar após 5 segundos
        self.root.after(5000, lambda: self.status_label.config(text="🟢 Sistema pronto"))


if __name__ == "__main__":
    # Teste da aplicação
    root = tb.Window(themename="darkly")
    app = MainApp(root)
    root.mainloop()
