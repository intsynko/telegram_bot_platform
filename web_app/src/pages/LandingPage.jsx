import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthModal from '../components/AuthModal';
import { BASE_URL } from "../config";

export default function LandingPage({ setUser }) {
  const navigate = useNavigate();
  const [user, setLocalUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [loading, setLoading] = useState(true);

  // Проверяем авторизацию пользователя
  useEffect(() => {
    fetch(`${BASE_URL}/api/users/auth/user/`, {
      credentials: 'include',
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.email) {
          setLocalUser(data);
          setUser(data); // Обновляем глобальное состояние
        }
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [setUser]);

  // Функция для обработки кликов по кнопкам
  const handleButtonClick = (path) => {
    if (user) {
      // Если пользователь авторизован, переходим по пути
      navigate(path);
    } else {
      // Если не авторизован, показываем модалку входа
      setShowAuthModal(true);
    }
  };

  // Обработчик успешной авторизации
  const handleAuthSuccess = (userData) => {
    setLocalUser(userData);
    setUser(userData); // Обновляем глобальное состояние в App.js
    setShowAuthModal(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Hero Section */}
      <div style={{ 
        padding: '80px 20px', 
        textAlign: 'center', 
        color: '#fff',
        maxWidth: 1200,
        margin: '0 auto'
      }}>
        <h1 style={{ 
          fontSize: '3.5rem', 
          fontWeight: '700', 
          marginBottom: '24px',
          textShadow: '0 2px 4px rgba(0,0,0,0.3)'
        }}>
          TG Bot Master
        </h1>
        <p style={{ 
          fontSize: '1.5rem', 
          marginBottom: '40px',
          opacity: 0.9,
          maxWidth: 800,
          marginLeft: 'auto',
          marginRight: 'auto',
          lineHeight: 1.6
        }}>
          Создавайте мощные Telegram-боты без программирования. 
          Визуальный конструктор форм, готовые шаблоны и простое управление.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button 
            onClick={() => handleButtonClick('/scenarios/templates')}
            style={{
              padding: '16px 32px',
              background: '#52c41a',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(82, 196, 26, 0.4)',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 20px rgba(82, 196, 26, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(82, 196, 26, 0.4)';
            }}>
            Начать создание
          </button>
          <button 
            onClick={() => handleButtonClick('/bots')}
            style={{
              padding: '16px 32px',
              background: 'rgba(255,255,255,0.2)',
              color: '#fff',
              border: '2px solid rgba(255,255,255,0.3)',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255,255,255,0.3)';
              e.target.style.borderColor = 'rgba(255,255,255,0.5)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255,255,255,0.2)';
              e.target.style.borderColor = 'rgba(255,255,255,0.3)';
            }}>
            Управление ботами
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ 
        background: '#fff', 
        padding: '80px 20px',
        position: 'relative'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <h2 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem', 
            marginBottom: '60px',
            color: '#333',
            fontWeight: '600'
          }}>
            Возможности платформы
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
            gap: '40px',
            marginBottom: '60px'
          }}>
            {/* Feature 1 */}
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: '#fff',
              boxShadow: '0 8px 32px rgba(240, 147, 251, 0.3)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎨</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px', fontWeight: '600' }}>
                Визуальный конструктор
              </h3>
              <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>
                Создавайте сложные формы и меню, перетаскивая элементы. 
                Никакого программирования - только интуитивный интерфейс.
              </p>
            </div>

            {/* Feature 2 */}
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: '#fff',
              boxShadow: '0 8px 32px rgba(79, 172, 254, 0.3)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📋</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px', fontWeight: '600' }}>
                Готовые шаблоны
              </h3>
              <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>
                Используйте готовые шаблоны для быстрого старта. 
                Адаптируйте их под свои нужды или создавайте с нуля.
              </p>
            </div>

            {/* Feature 3 */}
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              color: '#fff',
              boxShadow: '0 8px 32px rgba(67, 233, 123, 0.3)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🤖</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px', fontWeight: '600' }}>
                Управление ботами
              </h3>
              <p style={{ fontSize: '1.1rem', opacity: 0.9, lineHeight: 1.6 }}>
                Создавайте и управляйте множеством ботов. 
                Запускайте, останавливайте и мониторьте их работу.
              </p>
            </div>
          </div>

          {/* How it works */}
          <div style={{ 
            background: '#f8f9fa', 
            padding: '60px 40px', 
            borderRadius: '20px',
            textAlign: 'center'
          }}>
            <h3 style={{ 
              fontSize: '2rem', 
              marginBottom: '40px',
              color: '#333',
              fontWeight: '600'
            }}>
              Как это работает?
            </h3>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '30px',
              marginBottom: '40px'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  width: '80px', 
                  height: '80px', 
                  background: '#1890ff', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '2rem',
                  color: '#fff',
                  margin: '0 auto 20px',
                  fontWeight: 'bold'
                }}>
                  1
                </div>
                <h4 style={{ fontSize: '1.2rem', marginBottom: '12px', color: '#333' }}>
                  Создайте сценарий
                </h4>
                <p style={{ color: '#666', lineHeight: 1.5 }}>
                  Используйте визуальный конструктор для создания форм и меню
                </p>
              </div>

              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  width: '80px', 
                  height: '80px', 
                  background: '#52c41a', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '2rem',
                  color: '#fff',
                  margin: '0 auto 20px',
                  fontWeight: 'bold'
                }}>
                  2
                </div>
                <h4 style={{ fontSize: '1.2rem', marginBottom: '12px', color: '#333' }}>
                  Назначьте боту
                </h4>
                <p style={{ color: '#666', lineHeight: 1.5 }}>
                  Привяжите сценарий к вашему Telegram-боту
                </p>
              </div>

              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  width: '80px', 
                  height: '80px', 
                  background: '#faad14', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '2rem',
                  color: '#fff',
                  margin: '0 auto 20px',
                  fontWeight: 'bold'
                }}>
                  3
                </div>
                <h4 style={{ fontSize: '1.2rem', marginBottom: '12px', color: '#333' }}>
                  Запустите и используйте
                </h4>
                <p style={{ color: '#666', lineHeight: 1.5 }}>
                  Бот готов к работе! Управляйте им через панель
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div style={{ 
        background: '#f8f9fa', 
        padding: '80px 20px'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <h2 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem', 
            marginBottom: '60px',
            color: '#333',
            fontWeight: '600'
          }}>
            Для чего подходит платформа?
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '30px'
          }}>
            <div style={{ 
              background: '#fff', 
              padding: '30px', 
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              border: '1px solid #e8e8e8'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🏢</div>
              <h4 style={{ fontSize: '1.3rem', marginBottom: '12px', color: '#333' }}>
                Бизнес и услуги
              </h4>
              <p style={{ color: '#666', lineHeight: 1.6 }}>
                Онлайн-заказы, бронирования, консультации, 
                сбор заявок и обратная связь с клиентами
              </p>
            </div>

            <div style={{ 
              background: '#fff', 
              padding: '30px', 
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              border: '1px solid #e8e8e8'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🎓</div>
              <h4 style={{ fontSize: '1.3rem', marginBottom: '12px', color: '#333' }}>
                Образование
              </h4>
              <p style={{ color: '#666', lineHeight: 1.6 }}>
                Тесты, опросы, регистрация на курсы, 
                сбор домашних заданий и обратная связь
              </p>
            </div>

            <div style={{ 
              background: '#fff', 
              padding: '30px', 
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              border: '1px solid #e8e8e8'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🎯</div>
              <h4 style={{ fontSize: '1.3rem', marginBottom: '12px', color: '#333' }}>
                Опросы и голосования
              </h4>
              <p style={{ color: '#666', lineHeight: 1.6 }}>
                Маркетинговые исследования, голосования, 
                сбор мнений и статистика ответов
              </p>
            </div>

            <div style={{ 
              background: '#fff', 
              padding: '30px', 
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              border: '1px solid #e8e8e8'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🛒</div>
              <h4 style={{ fontSize: '1.3rem', marginBottom: '12px', color: '#333' }}>
                E-commerce
              </h4>
              <p style={{ color: '#666', lineHeight: 1.6 }}>
                Каталоги товаров, корзина покупок, 
                оформление заказов и отслеживание доставки
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
        padding: '80px 20px',
        textAlign: 'center',
        color: '#fff'
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <h2 style={{ 
            fontSize: '2.5rem', 
            marginBottom: '24px',
            fontWeight: '600'
          }}>
            Готовы создать своего бота?
          </h2>
          <p style={{ 
            fontSize: '1.2rem', 
            marginBottom: '40px',
            opacity: 0.9,
            lineHeight: 1.6
          }}>
            Присоединяйтесь к тысячам пользователей, которые уже создают 
            мощных Telegram-ботов без программирования
          </p>
          <button 
            onClick={() => handleButtonClick('/scenarios/templates')}
            style={{
              padding: '18px 40px',
              background: '#52c41a',
              color: '#fff',
              border: 'none',
              borderRadius: '10px',
              fontSize: '20px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              boxShadow: '0 6px 20px rgba(82, 196, 26, 0.4)',
              display: 'inline-block',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-3px)';
              e.target.style.boxShadow = '0 8px 25px rgba(82, 196, 26, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 6px 20px rgba(82, 196, 26, 0.4)';
            }}>
            Создать первого бота бесплатно
          </button>
        </div>
      </div>

      {/* Footer */}
      <div style={{ 
        background: '#2c3e50', 
        padding: '40px 20px',
        textAlign: 'center',
        color: '#bdc3c7'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <p style={{ fontSize: '1rem', marginBottom: '20px' }}>
            TG Bot Master - Платформа для создания Telegram-ботов
          </p>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '30px',
            flexWrap: 'wrap'
          }}>
            <Link to="/scenarios/templates" style={{ color: '#3498db', textDecoration: 'none' }}>
              Сценарии
            </Link>
            <Link to="/bots" style={{ color: '#3498db', textDecoration: 'none' }}>
              Боты
            </Link>
            <span style={{ color: '#7f8c8d' }}>|</span>
            <span>Поддержка</span>
            <span style={{ color: '#7f8c8d' }}>|</span>
            <span>Документация</span>
          </div>
        </div>
      </div>

      {/* Модалка авторизации */}
      <AuthModal
        open={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        setUser={handleAuthSuccess}
      />
    </div>
  );
} 