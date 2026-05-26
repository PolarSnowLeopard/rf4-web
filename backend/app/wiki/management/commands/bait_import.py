import json
from django.core.management.base import BaseCommand
from wiki.models import Bait


class Command(BaseCommand):
    help = '从JSON文件导入鱼饵数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='JSON文件的路径')
        parser.add_argument('--clear', action='store_true', help='导入前清空现有数据')
        parser.add_argument('--update', action='store_true', help='更新已存在的记录（按name匹配）')

    def handle(self, *args, **options):
        file_path = options['json_file']

        if options['clear']:
            deleted_count = Bait.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'已删除 {deleted_count} 条现有鱼饵数据'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                bait_data = json.load(file)

            created_count = 0
            updated_count = 0

            for item in bait_data:
                name = item.get('name', '')
                if not name:
                    continue

                fields = {
                    'description': item.get('description', ''),
                    'img': item.get('img', ''),
                    'bait_type': item.get('bait_type', ''),
                    'buoyancy': item.get('buoyancy', ''),
                    'weight': item.get('weight', ''),
                    'water_weight': item.get('water_weight', ''),
                    'hook_size': item.get('hook_size', ''),
                    'brand': item.get('brand', ''),
                    'size': item.get('size', ''),
                }

                bait_type = fields.pop('bait_type', '')
                lookup = {'name': name, 'bait_type': bait_type}
                fields_with_type = {**fields}

                if options['update']:
                    _, created = Bait.objects.update_or_create(
                        **lookup, defaults=fields_with_type,
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    _, created = Bait.objects.get_or_create(
                        **lookup, defaults=fields_with_type,
                    )
                    if created:
                        created_count += 1

            msg = f'导入完成: {created_count} 条新增'
            if updated_count:
                msg += f', {updated_count} 条更新'
            self.stdout.write(self.style.SUCCESS(msg))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'文件不存在: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('JSON格式错误'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入过程中发生错误: {str(e)}'))
