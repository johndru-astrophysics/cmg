TEMPLATE = """
#include <stdexcept>
#include "identifiable.hpp"
#include "index.hpp"

namespace {{schema.namespace}} {
    unsigned long Identifiable::getId() const
    {
        return id;
    }

    void Identifiable::setId(unsigned long id)
    {
        this->id = id;
    }

    void addToIndex(std::shared_ptr<Index> index)
    {
        throw std::runtime_error("Not implemented");
    }
}
"""
