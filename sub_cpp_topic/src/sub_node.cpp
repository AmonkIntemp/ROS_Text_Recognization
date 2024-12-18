#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"

class StringSubscriber : public rclcpp::Node {
public:
    StringSubscriber() : Node("string_subscriber") {
        subscription_ = this->create_subscription<example_interfaces::msg::String>(
            "string_topic", 10, std::bind(&StringSubscriber::callback, this, std::placeholders::_1));
    }

private:
    void callback(const example_interfaces::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "Received: '%s'", msg->data.c_str());
    }

    rclcpp::Subscription<example_interfaces::msg::String>::SharedPtr subscription_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<StringSubscriber>());
    rclcpp::shutdown();
    return 0;
}
