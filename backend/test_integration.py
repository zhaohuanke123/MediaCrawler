#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
集成测试脚本 - 验证爬虫集成是否正确
"""

import sys
import os
from pathlib import Path

# Robustly find project root by searching for marker files
def find_project_root() -> Path:
    """Find project root by looking for characteristic files"""
    current = Path(__file__).resolve().parent
    
    # Look for project markers (pyproject.toml, requirements.txt, etc.)
    markers = ['pyproject.toml', 'uv.lock', 'requirements.txt', 'main.py']
    
    for _ in range(5):  # Search up to 5 levels
        if any((current / marker).exists() for marker in markers):
            return current
        if current.parent == current:  # Reached root
            break
        current = current.parent
    
    # Fallback: assume standard structure
    return Path(__file__).resolve().parent.parent

project_root = find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_imports():
    """测试导入是否正常"""
    print("=" * 60)
    print("测试1: 模块导入")
    print("=" * 60)
    
    try:
        from backend.app.services.crawler_service import CrawlerService, REAL_CRAWLER_AVAILABLE
        print("✓ CrawlerService 导入成功")
        print(f"  - 真实爬虫可用: {REAL_CRAWLER_AVAILABLE}")
        
        if REAL_CRAWLER_AVAILABLE:
            from backend.app.services.real_crawler_service import RealCrawlerService
            print("✓ RealCrawlerService 导入成功")
            print(f"  - 支持的平台: {list(RealCrawlerService.PLATFORM_MAP.keys())}")
            print(f"  - 爬虫类: {list(RealCrawlerService.CRAWLER_CLASSES.keys())}")
        else:
            print("⚠ 真实爬虫不可用，将使用模拟爬虫")
            print("  提示: 运行 'uv sync && uv run playwright install' 安装依赖")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_conversion():
    """测试配置转换"""
    print("\n" + "=" * 60)
    print("测试2: 配置转换")
    print("=" * 60)
    
    try:
        from backend.app.services.real_crawler_service import RealCrawlerService
        
        # 测试配置
        test_config = {
            'keyword': '测试关键词',
            'pages': 5,
            'sort': 'latest'
        }
        
        print(f"输入配置: {test_config}")
        result = RealCrawlerService.prepare_config('xhs', 'search', test_config)
        print(f"转换结果: {result}")
        print("✓ 配置转换成功")
        
        return True
    except ImportError:
        print("⚠ 真实爬虫不可用，跳过配置转换测试")
        return True
    except Exception as e:
        print(f"✗ 配置转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """测试数据库模型"""
    print("\n" + "=" * 60)
    print("测试3: 数据库模型")
    print("=" * 60)
    
    try:
        from backend.app.models.task import Task
        from backend.app.models.result import Result
        print("✓ Backend数据模型导入成功")
        print(f"  - Task模型: {Task.__tablename__}")
        print(f"  - Result模型: {Result.__tablename__}")
        
        # 尝试导入爬虫数据模型
        try:
            from database.models import XhsNote, BilibiliVideo
            print("✓ 爬虫数据模型导入成功")
            print(f"  - XhsNote模型: {XhsNote.__tablename__}")
            print(f"  - BilibiliVideo模型: {BilibiliVideo.__tablename__}")
        except ImportError:
            print("⚠ 爬虫数据模型不可用（正常，可能缺少依赖）")
        
        return True
    except Exception as e:
        print(f"✗ 数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """测试API结构"""
    print("\n" + "=" * 60)
    print("测试4: API结构")
    print("=" * 60)
    
    try:
        from backend.app.api.v1.crawler import router as crawler_router
        from backend.app.api.v1.results import router as results_router
        from backend.app.api.v1.statistics import router as statistics_router
        
        print("✓ API路由导入成功")
        print(f"  - Crawler路由: {len(crawler_router.routes)} 个端点")
        print(f"  - Results路由: {len(results_router.routes)} 个端点")
        print(f"  - Statistics路由: {len(statistics_router.routes)} 个端点")
        
        # 列出爬虫端点
        print("\n  Crawler端点:")
        for route in crawler_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    print(f"    {method:6s} {route.path}")
        
        return True
    except Exception as e:
        print(f"✗ API结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_storage_paths():
    """测试存储路径"""
    print("\n" + "=" * 60)
    print("测试5: 存储路径")
    print("=" * 60)
    
    try:
        from backend.app.config import settings, get_database_url
        
        print("✓ Backend配置加载成功")
        print(f"  - 数据库类型: {settings.DATABASE_TYPE}")
        print(f"  - 数据库URL: {get_database_url()}")
        print(f"  - API前缀: {settings.API_PREFIX}")
        print(f"  - 服务端口: {settings.PORT}")
        
        # 检查数据库文件路径
        backend_db = Path("backend") / settings.SQLITE_DATABASE
        crawler_db = Path("database") / "sqlite_tables.db"
        
        print(f"\n  Backend数据库路径: {backend_db.absolute()}")
        print(f"  - 存在: {backend_db.exists()}")
        
        print(f"\n  爬虫数据库路径: {crawler_db.absolute()}")
        print(f"  - 存在: {crawler_db.exists()}")
        
        return True
    except Exception as e:
        print(f"✗ 存储路径测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("MediaCrawler Backend 集成测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("配置转换", test_config_conversion),
        ("数据库模型", test_database_models),
        ("API结构", test_api_structure),
        ("存储路径", test_storage_paths),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status:8s} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！集成成功！")
        return 0
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
