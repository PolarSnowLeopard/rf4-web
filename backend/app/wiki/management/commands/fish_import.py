import json
from django.core.management.base import BaseCommand
from wiki.models import Fish


class Command(BaseCommand):
    help = '从JSON文件导入鱼类数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='JSON文件的路径')
        parser.add_argument('--clear', action='store_true', help='导入前清空现有数据')
        parser.add_argument('--update', action='store_true', help='更新已存在的记录（按name匹配）')

    def handle(self, *args, **options):
        file_path = options['json_file']

        if options['clear']:
            deleted_count = Fish.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'已删除 {deleted_count} 条现有鱼类数据'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                fish_data = json.load(file)

            created_count = 0
            updated_count = 0

            for fish_item in fish_data:
                name = fish_item.get('name', '')
                if not name:
                    continue

                fields = {
                    'description': fish_item.get('description', ''),
                    'img': fish_item.get('img', ''),
                    'fish_class': fish_item.get('fish_class', ''),
                    'rare_weight': fish_item.get('rare_weight', ''),
                    'super_rare_weight': fish_item.get('super_rare_weight', ''),
                }

                if options['update']:
                    fish, created = Fish.objects.update_or_create(
                        name=name, defaults=fields,
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    _, created = Fish.objects.get_or_create(
                        name=name, defaults=fields,
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