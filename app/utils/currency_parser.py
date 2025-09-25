"""
Parser robusto para valores monetários brasileiros
Centralizado para evitar duplicação de código
"""
import re


class CurrencyParser:
    """Parser robusto para valores monetários brasileiros"""
    
    @staticmethod
    def to_float(value_str):
        """
        Converte string monetária para float
        Aceita: '10,50', '10.50', '1.234,56', 'R$ 25,90'
        """
        if not value_str or not str(value_str).strip():
            raise ValueError("Valor não pode estar vazio")
            
        # Limpar entrada
        clean = str(value_str).strip().upper()
        clean = clean.replace('R$', '').replace(' ', '')
        
        if not clean:
            raise ValueError("Valor não pode estar vazio")
        
        # Verificar se há sinal negativo
        if clean.startswith('-'):
            raise ValueError("Valor não pode ser negativo")
        
        # Remover caracteres não numéricos exceto vírgula e ponto
        clean = re.sub(r'[^\d,.]', '', clean)
        
        if not clean:
            raise ValueError("Formato inválido")
        
        # Determinar separador decimal
        if ',' in clean and '.' in clean:
            # Ambos presentes - último é decimal
            last_comma = clean.rfind(',')
            last_dot = clean.rfind('.')
            
            if last_comma > last_dot:
                # Vírgula depois do ponto - formato brasileiro
                clean = clean.replace('.', '').replace(',', '.')
            else:
                # Ponto depois da vírgula - formato americano modificado
                clean = clean.replace(',', '')
        elif ',' in clean:
            # Só vírgula - verificar se é decimal ou milhares
            comma_pos = clean.rfind(',')
            after_comma = clean[comma_pos + 1:]
            
            if len(after_comma) == 2:
                # Provavelmente decimal
                clean = clean.replace(',', '.')
            else:
                # Provavelmente separador de milhares
                clean = clean.replace(',', '')
        
        # Converter para float
        try:
            result = float(clean)
            if result < 0:
                raise ValueError("Valor não pode ser negativo")
            return result
        except ValueError:
            raise ValueError(f"Formato inválido: {value_str}")
    
    @staticmethod
    def to_string(value, decimal_places=2, currency_symbol=True):
        """
        Converte float para string monetária brasileira
        
        Args:
            value: Valor numérico
            decimal_places: Casas decimais (padrão 2)
            currency_symbol: Incluir símbolo R$ (padrão True)
            
        Returns:
            String formatada: "R$ 1.234,56" ou "1.234,56"
        """
        if not isinstance(value, (int, float)):
            raise ValueError("Valor deve ser numérico")
        
        if value < 0:
            raise ValueError("Valor não pode ser negativo")
        
        # Formatar com separadores brasileiros
        formatted = f"{value:,.{decimal_places}f}"
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        if currency_symbol:
            return f"R$ {formatted}"
        else:
            return formatted
    
    @staticmethod
    def to_brazilian(value):
        """Converte float para formato brasileiro (compatibilidade)"""
        try:
            return f"R$ {float(value):.2f}".replace('.', ',')
        except:
            return "R$ 0,00"

    @staticmethod
    def validate(value_str):
        """
        Valida se uma string pode ser convertida para moeda
        
        Args:
            value_str: String a ser validada
            
        Returns:
            bool: True se válida, False caso contrário
        """
        try:
            CurrencyParser.to_float(value_str)
            return True
        except ValueError:
            return False