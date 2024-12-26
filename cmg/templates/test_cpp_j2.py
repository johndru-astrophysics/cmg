TEMPLATE = """
#include <gtest/gtest.h>

{%- for include in schema.get_test_includes() %}
{{include}}
{%- endfor %}
using namespace {{schema.namespace}};

{%- for klass in schema.classes %}

class Test{{klass.name}} : public ::testing::Test
{
protected:
    void SetUp() override
    {
    {%- for field in klass.get_parent_fields() %}
        // Create parent object
        {{field.to_camel_case()}} = {{field._parent_klass.name}}::create({{field._parent_klass.get_example_arguments()}}){% if loop.index > 1 %}.lock()->getptr(){% endif %};
    {%- endfor %}
        // Create test object
    {%- if klass.has_parent() %}
        {{klass.get_var_name()}} = {{klass.name}}::create({{klass.get_example_arguments()}}).lock()->getptr();
    {%- else %}
        {{klass.get_var_name()}} = {{klass.name}}::create({{klass.get_example_arguments()}});
    {%- endif %}
    {%- for field in klass.get_ordered_fields() %}
        {%- if field.is_child %}
        auto child{{loop.index}} = {{field._child_klass.name}}::create({{field._child_klass.get_example_arguments()}}).lock()->getptr();
            {%- if field.is_list %}
        {{klass.get_var_name()}}->addTo{{field.to_camel_case(upper_first=True)}}(child{{loop.index}});
            {%- else %}
        {{klass.get_var_name()}}->set{{field.to_camel_case(upper_first=True)}}(child{{loop.index}});
            {%- endif %}
        {%- endif %}    
    {%- endfor %}


    }

    {%- for field in klass.get_parent_fields() %}
    std::shared_ptr<{{field._parent_klass.name}}> {{field.to_camel_case()}};
    {%- endfor %}
    std::shared_ptr<{{klass.name}}> {{klass.get_var_name()}};
};

{%- endfor %}

{%- for klass in schema.classes %}

TEST_F(Test{{klass.name}}, test_create)
{
    // Check object creation
    EXPECT_NE({{klass.get_var_name()}}, nullptr);
}

TEST_F(Test{{klass.name}}, test_update_exception)
{
    // Check exception thrown when updating with invalid field
    EXPECT_THROW(
        {
        try
        {
            {{klass.get_var_name()}}->update({%raw%}{{"missing", std::string("missing")}}{%endraw%});
        }
        catch (const std::invalid_argument &e)
        {
            // and this tests that it has the correct message
            EXPECT_STREQ("Invalid field: missing", e.what());
            throw;
        } }, std::invalid_argument);
}

TEST_F(Test{{klass.name}}, test_update)
{
    // Check object update
    {{klass.get_var_name()}}->update({{klass.get_example_update_arguments()}});
    {%- for field in klass.get_updatable_fields() %}
        {%- if field.get_example() != "nullptr" %}
            {%- if field.has_parent() %}
    EXPECT_EQ({{klass.get_var_name()}}->get{{field.to_camel_case(upper_first=True)}}().lock(), {{field.get_example()}});
            {%- else %}
    EXPECT_EQ({{klass.get_var_name()}}->get{{field.to_camel_case(upper_first=True)}}(), {{field.get_example()}});
            {%- endif %}
        {%- endif %}
    {%- endfor %}

    {%- if klass.has_parent() %}
    
    // Test parent field
        {%- for field in klass.get_parent_fields() %}
    auto other{{field.to_camel_case(upper_first=True)}} = {{field._parent_klass.name}}::create({{field._parent_klass.get_example_arguments()}}){% if loop.index > 1 %}.lock()->getptr(){% endif %};
        {%- endfor %}
    {%- set parent_field = klass.get_parent_field() %}
    {%- set parent_field_name = parent_field.to_camel_case() %}
    {%- set parent_field_name_title = parent_field.to_camel_case(upper_first=True) %}
    {{klass.get_var_name()}}->update({%raw%}{{{%endraw%}"{{parent_field_name}}", other{{parent_field_name_title}}{%raw%}}}{%endraw%});
    EXPECT_EQ({{klass.get_var_name()}}->get{{parent_field_name_title}}().lock(), other{{parent_field_name_title}});
        {%- if parent_field._parent_field.is_list %}
    EXPECT_EQ(other{{parent_field_name_title}}->get{{parent_field._parent_field.to_camel_case(upper_first=True)}}().size(), 1);
    EXPECT_EQ({{parent_field_name}}->get{{parent_field._parent_field.to_camel_case(upper_first=True)}}().size(), 0);
        {%- else %}
    EXPECT_EQ(other{{parent_field_name_title}}->get{{parent_field._parent_field.to_camel_case(upper_first=True)}}(), {{klass.get_var_name()}});
    EXPECT_EQ({{parent_field_name}}->get{{parent_field._parent_field.to_camel_case(upper_first=True)}}(), nullptr);
        {%- endif %}
    {%- endif %}

}

    {%- for field in klass.get_updatable_fields() %}
        {% if field.get_example() != "nullptr" and not field.has_parent() %}
TEST_F(Test{{klass.name}}, test_{{field.to_camel_case()}})
{
    // Check object update
    {{klass.get_var_name()}}->set{{field.to_camel_case(upper_first=True)}}({{field.get_example()}});
    EXPECT_EQ({{klass.get_var_name()}}->get{{field.to_camel_case(upper_first=True)}}(), {{field.get_example()}});
}
        {% endif %}
    {%- endfor %}

TEST_F(Test{{klass.name}}, test_destroy)
{
    // Check object destruction
    {{klass.get_var_name()}}->destroy();
}


{%- endfor %}


#include <cstdlib>

class ShellCommandEnvironment : public ::testing::Environment {
public:
    ~ShellCommandEnvironment() override {
        // Run shell commands after all tests
        system("echo All tests finished");
        system("llvm-profdata merge -o default.profdata default.profraw");
        system("llvm-cov export --format=lcov --instr-profile default.profdata test_{{schema.namespace}}.exe --sources {{schema.get_lcov_src()}} > lcov.info");
        system("llvm-cov report --instr-profile default.profdata --ignore-filename-regex='.*_deps.*' test_{{schema.namespace}}.exe --sources {{schema.get_lcov_src()}}");
    }
};

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    ::testing::AddGlobalTestEnvironment(new ShellCommandEnvironment);
    return RUN_ALL_TESTS();
}
"""
