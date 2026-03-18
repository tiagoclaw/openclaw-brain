"""
Cache Manager - Sistema de cache em memória para MVP
Migrar para Redis quando escalar para produção
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# TTLs por tipo de dado (em segundos)
CACHE_TTL = {
    "bcb_sgs": 3600,        # 1 hora - dados macro atualizam 1x/dia
    "bcb_focus": 7200,      # 2 horas - Focus atualiza 1x/semana
    "b3_quote": 300,        # 5 minutos - cotações mudam constantemente
    "tesouro": 3600,        # 1 hora - taxas atualizam de manhã
    "ibge": 86400,          # 24 horas - dados IBGE são mensais
    "cvm_fundos": 86400,    # 24 horas - NAV atualiza 1x/dia
    "default": 1800,        # 30 minutos para dados não classificados
}

class CacheManager:
    """
    Cache em memória simples para MVP.
    Thread-safe básico com controle de TTL por tipo de fonte.
    """
    
    def __init__(self):
        self._store = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "errors": 0
        }
        logger.info("Cache Manager iniciado (in-memory)")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera item do cache se ainda válido.
        
        Args:
            key: Chave única do item
            
        Returns:
            Dados cacheados ou None se expirado/inexistente
        """
        try:
            if key in self._store:
                entry = self._store[key]
                current_time = time.time()
                
                if current_time < entry["expires_at"]:
                    self._stats["hits"] += 1
                    logger.debug(f"Cache HIT: {key}")
                    return entry["data"]
                else:
                    # Item expirado, remover
                    del self._store[key]
                    self._stats["evictions"] += 1
                    logger.debug(f"Cache EXPIRED: {key}")
            
            self._stats["misses"] += 1
            logger.debug(f"Cache MISS: {key}")
            return None
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Erro ao buscar cache {key}: {e}")
            return None
    
    def set(self, key: str, data: Dict[str, Any], source_type: str = "default") -> bool:
        """
        Armazena item no cache com TTL baseado no tipo da fonte.
        
        Args:
            key: Chave única do item
            data: Dados para cachear (deve ser serializável)
            source_type: Tipo da fonte para determinar TTL
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            ttl = CACHE_TTL.get(source_type, CACHE_TTL["default"])
            expires_at = time.time() + ttl
            
            self._store[key] = {
                "data": data,
                "expires_at": expires_at,
                "cached_at": time.time(),
                "source_type": source_type,
                "ttl": ttl
            }
            
            self._stats["sets"] += 1
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s, tipo: {source_type})")
            return True
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Erro ao salvar cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove item específico do cache."""
        try:
            if key in self._store:
                del self._store[key]
                logger.debug(f"Cache DELETE: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    def clear(self) -> int:
        """
        Limpa todo o cache.
        
        Returns:
            Número de itens removidos
        """
        try:
            count = len(self._store)
            self._store.clear()
            logger.info(f"Cache limpo: {count} itens removidos")
            return count
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        """
        Remove itens expirados do cache.
        
        Returns:
            Número de itens removidos
        """
        try:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._store.items()
                if current_time >= entry["expires_at"]
            ]
            
            for key in expired_keys:
                del self._store[key]
            
            removed_count = len(expired_keys)
            if removed_count > 0:
                self._stats["evictions"] += removed_count
                logger.info(f"Cache cleanup: {removed_count} itens expirados removidos")
                
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro ao limpar itens expirados: {e}")
            return 0
    
    def stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dict com métricas de uso do cache
        """
        try:
            current_time = time.time()
            
            # Contar itens ativos (não expirados)
            active_items = sum(
                1 for entry in self._store.values()
                if current_time < entry["expires_at"]
            )
            
            # Estatísticas por tipo
            by_type = {}
            total_size_estimate = 0
            
            for entry in self._store.values():
                if current_time < entry["expires_at"]:
                    source_type = entry.get("source_type", "unknown")
                    by_type[source_type] = by_type.get(source_type, 0) + 1
                    
                    # Estimativa grosseira do tamanho
                    try:
                        size = len(json.dumps(entry["data"]))
                        total_size_estimate += size
                    except:
                        pass
            
            hit_rate = 0
            if self._stats["hits"] + self._stats["misses"] > 0:
                hit_rate = self._stats["hits"] / (self._stats["hits"] + self._stats["misses"])
            
            return {
                "total_keys": len(self._store),
                "active_items": active_items,
                "expired_items": len(self._store) - active_items,
                "by_type": by_type,
                "size_estimate_bytes": total_size_estimate,
                "hit_rate": round(hit_rate, 3),
                "statistics": self._stats.copy(),
                "ttl_config": CACHE_TTL.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return {"erro": str(e)}
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """
        Gera chave de cache consistente.
        
        Args:
            prefix: Prefixo identificando o tipo de dados
            *args: Argumentos que identificam unicamente a requisição
            
        Returns:
            Chave de cache como string
        """
        # Normalizar argumentos para string
        normalized_args = []
        for arg in args:
            if isinstance(arg, (str, int, float)):
                normalized_args.append(str(arg).lower())
            elif arg is None:
                normalized_args.append("none")
            else:
                normalized_args.append(str(arg))
        
        # Criar chave única
        key = f"{prefix}::{':'.join(normalized_args)}"
        return key.replace(" ", "_")

# Singleton global para usar em toda aplicação
cache = CacheManager()

# Decorator para cache automático
def cached(source_type: str = "default", key_prefix: str = ""):
    """
    Decorator para cache automático de funções async.
    
    Args:
        source_type: Tipo da fonte para TTL
        key_prefix: Prefixo para chave de cache
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            cache_key = cache.get_cache_key(
                key_prefix or func.__name__, 
                *args, 
                *[f"{k}={v}" for k, v in sorted(kwargs.items())]
            )
            
            # Tentar cache primeiro
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função se não está em cache
            try:
                result = await func(*args, **kwargs)
                
                # Cachear resultado se não há erro
                if "erro" not in result:
                    cache.set(cache_key, result, source_type)
                
                return result
                
            except Exception as e:
                logger.error(f"Erro na função cacheada {func.__name__}: {e}")
                return {"erro": str(e)}
        
        return wrapper
    return decorator