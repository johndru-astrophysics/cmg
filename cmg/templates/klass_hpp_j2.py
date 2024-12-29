TEMPLATE = """

#ifndef {{klass.get_include_define()}}
#define {{klass.get_include_define()}}

#include <any>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace {{schema.namespace}}
{
{%- for forward in klass.get_forward_declarations() %}
    class {{forward}};
{%- endfor %}


    /**
        @brief {{klass.description}}

{%- for field in klass.get_ordered_fields() %}
        @param {{field.to_camel_case()}} ({{field.get_cpp_type()}}) {{field.description}}.{% if field.has_default() %} Defaults to {{field.default}}.{% endif %}
{%- endfor %}
    */

    class {{klass.name}} : public std::enable_shared_from_this<{{klass.name}}>
    {
        struct PrivateConstructor
        {
            PrivateConstructor() = default;
        };

{%- for field in klass.get_ordered_fields() %}
        {{field.get_cpp_type()}} {{field.to_camel_case()}}{% if field.has_default() %} = {{field.default}}{% endif %};
{%- endfor %}

    public:
        {{klass.name}}(PrivateConstructor) {}

        /**
            @brief Create a new {{klass.name}} object
{%- for field in klass.init_fields() %}
            @param {{field.to_camel_case()}} {{field.description}}
{%- endfor %}
            @return A pointer to the new object
        */
        static {{klass.get_create_ptr_type()}} create({{klass.get_create_arguments()}});

        /**
            @brief Update the object with new values
            @param fields A map of field names to new values
        */
        void update(std::map<std::string, std::any> fields);

        /**
            @brief Destroy the object and remove it from parent objects, also removes all child objects
        */
        void destroy(bool fromParent = false);

        {{klass.name}}() : {{klass.name}}(PrivateConstructor()) {}

        /**
            @brief Get a shared pointer to the object, use this instead of make_shared
            @return A shared pointer to the object
        */
        std::shared_ptr<{{klass.name}}> getptr();

{%- for field in klass.get_ordered_fields() %}
    {%- if field.has_parent(): %}
        /**
            @brief Set this object for
        */
        void reset{{field.to_camel_case(upper_first=True)}}();
    {%- endif %}
    {% if field.is_list %}
        {%- if field.child_field %}
        /**
            @brief Add an item to the list of {{field.to_camel_case()}}
            @param item The item to add
            @param fromChild True if this is called from the child object
        */
        void addTo{{field.to_camel_case(upper_first=True)}}({{field.get_cpp_type(nolist=True)}} item, bool fromChild = false);

        /**
            @brief Remove an item from the list of {{field.to_camel_case()}}
            @param item The item to remove
            @param fromChild True if this is called from the child object
        */
        void removeFrom{{field.to_camel_case(upper_first=True)}}({{field.get_cpp_type(nolist=True)}} item, bool fromChild = false);
        {%- else %}

        /**  
            @brief Add an item to the list of {{field.to_camel_case()}}
            @param item The item to add
        */
        void addTo{{field.to_camel_case(upper_first=True)}}({{field.get_cpp_type(nolist=True)}} item, bool fromChild = false);
        
        /**
            @brief Remove an item from the list of {{field.to_camel_case()}}
            @param item The item to remove
        */
        void removeFrom{{field.to_camel_case(upper_first=True)}}({{field.get_cpp_type(nolist=True)}} item, bool fromChild = false);
        {%- endif %}
    {% else %}
        /**
            @brief Set the value of {{field.to_camel_case()}}
            @param {{field.to_camel_case()}} The new value
        */
        void set{{field.to_camel_case(upper_first=True)}}({{field.get_cpp_type()}} {{field.to_camel_case()}});
    {% endif %}
    
        /**
            @brief Get the value of {{field.to_camel_case()}}
            @return The value of {{field.to_camel_case()}}
        */
        {{field.get_cpp_type()}} get{{field.to_camel_case(upper_first=True)}}();

{%- endfor %}

    };
}
#endif
"""
