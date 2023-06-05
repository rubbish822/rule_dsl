You can make execution rules for databases, such as mysql, postgresql, redis, clickhouse, etc.

# Grammar:
```
if
Condition 1
then
    Action 1
elseif
    Condition 2
then
    Action 2
else
    Action 3
end
```

# Example:
    ```
    1. str:
        '''
        if
        @fac.sql_type == "select"
        then
        @act.allow_execute "allow test ok"
        end
        '''
    2. int or float:
        '''
        if
        @fac.is_admin_user == 1 and @fun.is_char_lower(@fac.sql_type)
        then
        @act.allow_execute
        end
        '''
    3. list or dict:
        '''
        if
        @fac.sql_type in ["select","update"] or "address" not in {"name": "tom", "age": 18}
        then
        @act.allow_execute
        end
        '''
    4. regex:
        ```
        if
        @fac.user matchs "ops_\\w+"
        then
        @act.allow_execute
        end
        ```
[see more](./dsl/tests.py)
